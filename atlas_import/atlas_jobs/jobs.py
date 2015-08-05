import csv
import logging
import os
from django.conf import settings

from django.contrib.gis.geos import GEOSGeometry, Point
from elasticsearch_dsl.connections import connections

from atlas import models, documents
from . import uva2

log = logging.getLogger(__name__)


def merge(model, pk, values):
    model.objects.update_or_create(pk=pk, defaults=values)


def merge_existing(model, pk, values):
    model.objects.filter(pk=pk).update(**values)


def foreign_key(model, key):
    if not key:
        return None

    try:
        return model.objects.get(pk=key)
    except model.DoesNotExist:
        log.warning("Could not load object of type %s with key %s", model, key)
        return None


class AbstractUvaTask(object):
    code = None

    def __init__(self, source):
        self.source = uva2.resolve_file(source, self.code)

    def execute(self):
        with uva2.uva_reader(self.source) as rows:
            for r in rows:
                self.process_row(r)

    def process_row(self, r):
        raise NotImplementedError()


class CodeOmschrijvingUvaTask(AbstractUvaTask):
    model = None

    def process_row(self, r):
        merge(self.model, r['Code'], dict(
            omschrijving=r['Omschrijving']
        ))


class AbstractGeoTask(object):
    source_file = None

    def __init__(self, source_path):
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter='|')
            for row in rows:
                self.process_row(row[0], GEOSGeometry(row[1]))

    def process_row(self, row_id, geom):
        raise NotImplementedError()


class ImportBrnTask(CodeOmschrijvingUvaTask):
    name = "import BRN"
    code = "BRN"
    model = models.Bron


class ImportAvrTask(CodeOmschrijvingUvaTask):
    name = "import AVR"
    code = "AVR"
    model = models.RedenAfvoer


class ImportStsTask(CodeOmschrijvingUvaTask):
    name = "import STS"
    code = "STS"
    model = models.Status


class ImportEgmTask(CodeOmschrijvingUvaTask):
    name = "import EGM"
    code = "EGM"
    model = models.Eigendomsverhouding


class ImportFngTask(CodeOmschrijvingUvaTask):
    name = "import FNG"
    code = "FNG"
    model = models.Financieringswijze


class ImportLggTask(CodeOmschrijvingUvaTask):
    name = "import LGG"
    code = "LGG"
    model = models.Ligging


class ImportGbkTask(CodeOmschrijvingUvaTask):
    name = "import GBK"
    code = "GBK"
    model = models.Gebruik


class ImportLocTask(CodeOmschrijvingUvaTask):
    name = "import LOC"
    code = "LOC"
    model = models.LocatieIngang


class ImportTggTask(CodeOmschrijvingUvaTask):
    name = "import TGG"
    code = "TGG"
    model = models.Toegang


class ImportGmeTask(AbstractUvaTask):
    name = "import GME"
    code = "GME"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        merge(models.Gemeente, r['sleutelVerzendend'], dict(
            code=r['Gemeentecode'],
            naam=r['Gemeentenaam'],
            verzorgingsgebied=uva2.uva_indicatie(r['IndicatieVerzorgingsgebied']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class ImportSdlTask(AbstractUvaTask):
    name = "import SDL"
    code = "SDL"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['SDLGME/TijdvakRelatie/begindatumRelatie'],
                               r['SDLGME/TijdvakRelatie/einddatumRelatie']):
            return

        merge(models.Stadsdeel, r['sleutelVerzendend'], dict(
            code=r['Stadsdeelcode'],
            naam=r['Stadsdeelnaam'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente=models.Gemeente.objects.get(pk=r['SDLGME/GME/sleutelVerzendend']),
        ))


class ImportBrtTask(AbstractUvaTask):
    name = "import BRT"
    code = "BRT"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['BRTSDL/TijdvakRelatie/begindatumRelatie'],
                               r['BRTSDL/TijdvakRelatie/einddatumRelatie']):
            return

        merge(models.Buurt, r['sleutelVerzendend'], dict(
            code=r['Buurtcode'],
            naam=r['Buurtnaam'],
            stadsdeel=models.Stadsdeel.objects.get(pk=r['BRTSDL/SDL/sleutelVerzendend']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class ImportWplTask(AbstractUvaTask):
    name = "import WPL"
    code = "WPL"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'WPLGME'):
            return

        merge(models.Woonplaats, r['sleutelverzendend'], dict(
            code=r['Woonplaatsidentificatie'],
            naam=r['Woonplaatsnaam'],
            document_nummer=r['DocumentnummerMutatieWoonplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieWoonplaats']),
            naam_ptt=r['WoonplaatsPTTSchrijfwijze'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente=foreign_key(models.Gemeente, r['WPLGME/GME/sleutelVerzendend']),
        ))


class ImportOprTask(AbstractUvaTask):
    name = "import OPR"
    code = "OPR"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'OPRBRN', 'OPRSTS', 'OPRWPL'):
            return

        merge(models.OpenbareRuimte, r['sleutelVerzendend'], dict(
            type=r['TypeOpenbareRuimteDomein'],
            naam=r['NaamOpenbareRuimte'],
            code=r['Straatcode'],
            document_nummer=r['DocumentnummerMutatieOpenbareRuimte'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieOpenbareRuimte']),
            straat_nummer=r['Straatnummer'],
            naam_nen=r['StraatnaamNENSchrijfwijze'],
            naam_ptt=r['StraatnaamPTTSchrijfwijze'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron=foreign_key(models.Bron, r['OPRBRN/BRN/Code']),
            status=foreign_key(models.Status, r['OPRSTS/STS/Code']),
            woonplaats=foreign_key(models.Woonplaats, r['OPRWPL/WPL/sleutelVerzendend']),
        ))


class ImportNumTask(AbstractUvaTask):
    name = "import NUM"
    code = "NUM"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMBRN', 'NUMSTS', 'NUMOPR'):
            return

        merge(models.Nummeraanduiding, r['sleutelVerzendend'], dict(
            code=r['IdentificatiecodeNummeraanduiding'],
            huisnummer=r['Huisnummer'],
            huisletter=r['Huisletter'],
            huisnummer_toevoeging=r['Huisnummertoevoeging'],
            postcode=r['Postcode'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieNummeraanduiding']),
            document_nummer=r['DocumentnummerMutatieNummeraanduiding'],
            type=r['TypeAdresseerbaarObjectDomein'],
            adres_nummer=r['Adresnummer'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron=foreign_key(models.Bron, r['NUMBRN/BRN/Code']),
            status=foreign_key(models.Status, r['NUMSTS/STS/Code']),
            openbare_ruimte=foreign_key(models.OpenbareRuimte, r['NUMOPR/OPR/sleutelVerzendend']),
        ))


class ImportLigTask(AbstractUvaTask):
    name = "import LIG"
    code = "LIG"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'LIGBRN', 'LIGSTS', 'LIGBRT'):
            return

        merge(models.Ligplaats, r['sleutelverzendend'], dict(
            identificatie=r['Ligplaatsidentificatie'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieLigplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieLigplaats']),
            bron=foreign_key(models.Bron, r['LIGBRN/BRN/Code']),
            status=foreign_key(models.Status, r['LIGSTS/STS/Code']),
            buurt=foreign_key(models.Buurt, r['LIGBRT/BRT/sleutelVerzendend'])
        ))


class ImportNumLigHfdTask(AbstractUvaTask):
    name = "import NUMLIGHFD"
    code = "NUMLIGHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMLIGHFD'):
            return

        merge_existing(models.Ligplaats, r['NUMLIGHFD/LIG/sleutelVerzendend'], dict(
            hoofdadres=foreign_key(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportStaTask(AbstractUvaTask):
    name = "import STA"
    code = "STA"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'STABRN', 'STASTS', 'STABRT'):
            return

        merge(models.Standplaats, r['sleutelverzendend'], dict(
            identificatie=r['Standplaatsidentificatie'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieStandplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieStandplaats']),
            bron=foreign_key(models.Bron, r['STABRN/BRN/Code']),
            status=foreign_key(models.Status, r['STASTS/STS/Code']),
            buurt=foreign_key(models.Buurt, r['STABRT/BRT/sleutelVerzendend'])
        ))


class ImportNumStaHfdTask(AbstractUvaTask):
    name = "import NUMSTAHFD"
    code = "NUMSTAHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMSTAHFD'):
            return

        merge_existing(models.Standplaats, r['NUMSTAHFD/STA/sleutelVerzendend'], dict(
            hoofdadres=foreign_key(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportVboTask(AbstractUvaTask):
    name = "import VBO"
    code = "VBO"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'VBOAVR', 'VBOBRN', 'VBOEGM', 'VBOFNG', 'VBOGBK', 'VBOLOC', 'VBOLGG', 'VBOMNT',
                                     'VBOTGG', 'VBOOVR', 'VBOSTS', 'VBOBRT'):
            return

        x = r['X-Coordinaat']
        y = r['Y-Coordinaat']
        if x and y:
            geo = Point(int(x), int(y))
        else:
            geo = None

        merge(models.Verblijfsobject, r['sleutelverzendend'], dict(
            identificatie=(r['Verblijfsobjectidentificatie']),
            geometrie=geo,
            gebruiksdoel_code=(r['GebruiksdoelVerblijfsobjectDomein']),
            gebruiksdoel_omschrijving=(r['OmschrijvingGebruiksdoelVerblijfsobjectDomein']),
            oppervlakte=uva2.uva_nummer(r['OppervlakteVerblijfsobject']),
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieVerblijfsobject']),
            document_nummer=(r['DocumentnummerMutatieVerblijfsobject']),
            bouwlaag_toegang=uva2.uva_nummer(r['Bouwlaagtoegang']),
            status_coordinaat_code=(r['StatusCoordinaatDomein']),
            status_coordinaat_omschrijving=(r['OmschrijvingCoordinaatDomein']),
            bouwlagen=uva2.uva_nummer(r['AantalBouwlagen']),
            type_woonobject_code=(r['TypeWoonobjectDomein']),
            type_woonobject_omschrijving=(r['OmschrijvingTypeWoonobjectDomein']),
            woningvoorraad=uva2.uva_indicatie(r['IndicatieWoningvoorraad']),
            aantal_kamers=uva2.uva_nummer(r['AantalKamers']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            reden_afvoer=foreign_key(models.RedenAfvoer, r['VBOAVR/AVR/Code']),
            bron=foreign_key(models.Bron, r['VBOBRN/BRN/Code']),
            eigendomsverhouding=foreign_key(models.Eigendomsverhouding, r['VBOEGM/EGM/Code']),
            financieringswijze=foreign_key(models.Financieringswijze, r['VBOFNG/FNG/Code']),
            gebruik=foreign_key(models.Gebruik, r['VBOGBK/GBK/Code']),
            locatie_ingang=foreign_key(models.LocatieIngang, r['VBOLOC/LOC/Code']),
            ligging=foreign_key(models.Ligging, r['VBOLGG/LGG/Code']),
            # ?=(r['VBOMNT/MNT/Code']),
            toegang=foreign_key(models.Toegang, r['VBOTGG/TGG/Code']),
            # ?=(r['VBOOVR/OVR/Code']),
            status=foreign_key(models.Status, r['VBOSTS/STS/Code']),
            buurt=foreign_key(models.Buurt, r['VBOBRT/BRT/sleutelVerzendend']),
        ))


class ImportNumVboHfdTask(AbstractUvaTask):
    name = "import NUMVBOHFD"
    code = "NUMVBOHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBOHFD'):
            return

        merge_existing(models.Verblijfsobject, r['NUMVBOHFD/VBO/sleutelVerzendend'], dict(
            hoofdadres=foreign_key(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportPndTask(AbstractUvaTask):
    name = "import PND"
    code = "PND"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDSTS', 'PNDBBK'):
            return

        merge(models.Pand, r['sleutelverzendend'], dict(
            identificatie=(r['Pandidentificatie']),
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatiePand']),
            document_nummer=(r['DocumentnummerMutatiePand']),
            bouwjaar=uva2.uva_nummer(r['OorspronkelijkBouwjaarPand']),
            laagste_bouwlaag=uva2.uva_nummer(r['LaagsteBouwlaag']),
            hoogste_bouwlaag=uva2.uva_nummer(r['HoogsteBouwlaag']),
            pandnummer=(r['Pandnummer']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            status=foreign_key(models.Status, r['PNDSTS/STS/Code']),
            # x=(r['PNDBBK/BBK/Bouwbloknummer']),
        ))


class ImportPndVboTask(AbstractUvaTask):
    name = "import PNDVBO"
    code = "PNDVBO"

    def process_row(self, r):
        # todo: verwijderen panden die niet langer relevant zijn

        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDVBO'):
            return

        pand_id = r['sleutelverzendend']
        vbo_id = r['PNDVBO/VBO/sleutelVerzendend']

        try:
            models.Verblijfsobject.objects.get(pk=vbo_id).panden.add(models.Pand.objects.get(pk=pand_id))
        except models.Verblijfsobject.DoesNotExist:
            log.warn("Non-existing verblijfsobject: %s", vbo_id)

'''
class ImportBelemmeringTask(object):
    name = "Import belemmering"
    code = "belemmering"
    
    col_identificatie = 0
    col_inschrijfnummer = 1
    col_beperkingcode = 2
    col_datum_in_werking = 3
    col_datum_einde = 4

    def __init__(self, source_path):
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)
    
    def process_row(self, r):
        merge(models.Pand, r['sleutelverzendend'], dict(
            identificatie = r[col_identificatie],
            inschrijfnummer = r[col_inschrijfnummer],
            beperkingcode = r[col_beperkingcode],
            datum_in_werking = r[col_in_werking],
            datum_einde = r[col_datum_einde],
        ))
'''

class ImportBeperkingcodeTask(object):
    name = "import Beperkingcode"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_belemmeringcode.dat')
        
    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)
    
    def process_row(self, r):
        merge(models.Beperkingcode, r[0], dict(
            omschrijving = r[1],
        ))

class ImportWkpbBroncodeTask(object):
    name = "import Wkpb Broncode"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_broncode.dat')
        
    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)
    
    def process_row(self, r):
        merge(models.WkpbBroncode, r[0], dict(
            omschrijving = r[1],
        ))

class ImportWkpbBrondocumentTask(object):
    name = "import Wkpb Brondocument"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, 'wpb_brondocument.dat')
        
    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter=';')
            for row in rows:
                self.process_row(row)
    
    def process_row(self, r):
        if r[4] == '0':
            pers_afsch = False
        else:
            pers_afsch = True
        merge(models.WkpbBrondocument, r[0], dict(
            documentnummer = r[0],
            bron = foreign_key(models.WkpbBroncode, r[2]),
            documentnaam = r[3],
            persoonsgegeven_afschermen = pers_afsch,
            soort_besluit = r[5],
        ))





class ImportStaGeoTask(AbstractGeoTask):
    name = "import STA WKT"
    source_file = "BAG_STANDPLAATS_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        merge_existing(models.Standplaats, '0' + row_id, dict(
            geometrie=geom,
        ))



class ImportLigGeoTask(AbstractGeoTask):
    name = "import LIG WKT"
    source_file = "BAG_LIGPLAATS_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        merge_existing(models.Ligplaats, '0' + row_id, dict(
            geometrie=geom
        ))


class ImportPndGeoTask(AbstractGeoTask):
    name = "import PND WKT"
    source_file = "BAG_PAND_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        merge_existing(models.Pand, '0' + row_id, dict(
            geometrie=geom
        ))





class ImportELLigplaatsTask(object):
    name = "EL: import ligplaatsen"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Ligplaats.init()

    def execute(self):
        for l in models.Ligplaats.objects.all():
            doc = documents.from_ligplaats(l)
            doc.save()


class ImportELStandplaatsTask(object):
    name = "EL: import standplaatsen"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Standplaats.init()

    def execute(self):
        for s in models.Standplaats.objects.all():
            doc = documents.from_standplaats(s)
            doc.save()


class ImportELVerblijfsobjectTask(object):
    name = "EL: import verblijfsobjecten"

    def __init__(self):
        connections.create_connection(hosts=settings.ELASTIC_SEARCH_HOSTS)
        documents.Verblijfsobject.init()

    def execute(self):
        for v in models.Verblijfsobject.objects.all():
            doc = documents.from_verblijfsobject(v)
            doc.save()


class ImportJob(object):
    name = "atlas-import"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.bag = os.path.join(diva, 'bag')
        self.bag_wkt = os.path.join(diva, 'bag_wkt')
        self.gebieden = os.path.join(diva, 'gebieden')
        self.beperkingen = os.path.join(diva, 'beperkingen')

    def tasks(self):
        return [
            ImportAvrTask(self.bag),
            ImportBrnTask(self.bag),
            ImportEgmTask(self.bag),
            ImportFngTask(self.bag),
            ImportGbkTask(self.bag),
            ImportLggTask(self.bag),
            ImportLocTask(self.bag),
            ImportTggTask(self.bag),
            ImportStsTask(self.bag),

            ImportGmeTask(self.gebieden),
            ImportWplTask(self.bag),
            ImportSdlTask(self.gebieden),
            ImportBrtTask(self.gebieden),
            ImportOprTask(self.bag),
            ImportNumTask(self.bag),

            ImportLigTask(self.bag),
            ImportLigGeoTask(self.bag_wkt),
            ImportNumLigHfdTask(self.bag),

            ImportStaTask(self.bag),
            ImportStaGeoTask(self.bag_wkt),
            ImportNumStaHfdTask(self.bag),

            ImportVboTask(self.bag),
            ImportNumVboHfdTask(self.bag),

            ImportPndTask(self.bag),
            ImportPndGeoTask(self.bag_wkt),
            ImportPndVboTask(self.bag),
            
            ImportBeperkingcodeTask(self.beperkingen),
            ImportWkpbBroncodeTask(self.beperkingen),
            ImportWkpbBrondocumentTask(self.beperkingen),
        ]


class IndexJob(object):
    name = "atlas-index"

    def tasks(self):
        return [
            ImportELLigplaatsTask(),
            ImportELStandplaatsTask(),
            ImportELVerblijfsobjectTask(),
        ]
