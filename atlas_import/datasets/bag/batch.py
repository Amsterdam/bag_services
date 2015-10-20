import csv
import logging
import os
from abc import ABCMeta

from django.conf import settings

from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.gdal import DataSource

from datasets.generic import uva2, cache, index, mixins
from . import models, documents

log = logging.getLogger(__name__)
model_pk_code_mapping = {}


class CodeOmschrijvingUvaTask(uva2.AbstractUvaTask):
    model = None

    def process_row(self, r):
        # noinspection PyCallingNonCallable
        obj = self.model(pk=r['Code'], omschrijving=r['Omschrijving'])
        self.create(obj)


class ImportAvrTask(CodeOmschrijvingUvaTask):
    name = "import AVR"
    code = "AVR"
    model = models.RedenAfvoer


class ImportBrnTask(CodeOmschrijvingUvaTask):
    name = "import BRN"
    code = "BRN"
    model = models.Bron


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


class ImportGmeTask(uva2.AbstractUvaTask):
    name = "import GME"
    code = "GME"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        self.create(models.Gemeente(
            pk=r['sleutelVerzendend'],
            code=r['Gemeentecode'],
            naam=r['Gemeentenaam'],
            verzorgingsgebied=uva2.uva_indicatie(r['IndicatieVerzorgingsgebied']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class GeoModelCodePkMappingMixin(object):
    def get_pk(self, name, code):
        try:
            return model_pk_code_mapping[('%s-%s' % (name.lower(), code.lower()))]
        except KeyError:
            return

    def set_pk(self, name, code, pk):
        model_pk_code_mapping['%s-%s' % (name.lower(), code.lower())] = pk


class ImportSdlTask(GeoModelCodePkMappingMixin, uva2.AbstractUvaTask):
    name = "import SDL"
    code = "SDL"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['SDLGME/TijdvakRelatie/begindatumRelatie'],
                               r['SDLGME/TijdvakRelatie/einddatumRelatie']):
            return

        self.set_pk(models.Stadsdeel.__name__, r['Stadsdeelcode'], r['sleutelVerzendend'])

        self.create(models.Stadsdeel(
            pk=(r['sleutelVerzendend']),
            code=r['Stadsdeelcode'],
            naam=r['Stadsdeelnaam'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente_id=(self.foreign_key_id(models.Gemeente, r['SDLGME/GME/sleutelVerzendend'])),
        ))


class ImportBrtTask(GeoModelCodePkMappingMixin, uva2.AbstractUvaTask):
    name = "import BRT"
    code = "BRT"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['BRTSDL/TijdvakRelatie/begindatumRelatie'],
                               r['BRTSDL/TijdvakRelatie/einddatumRelatie']):
            return

        self.set_pk(models.Buurt.__name__, r['Buurtcode'], r['sleutelVerzendend'])

        self.create(models.Buurt(
            pk=r['sleutelVerzendend'],
            code=r['Buurtcode'],
            naam=r['Buurtnaam'],
            stadsdeel_id=self.foreign_key_id(models.Stadsdeel, r['BRTSDL/SDL/sleutelVerzendend']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class ImportBbkTask(GeoModelCodePkMappingMixin, uva2.AbstractUvaTask):
    name = "import BBK"
    code = "BBK"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['BBKBRT/TijdvakRelatie/begindatumRelatie'],
                               r['BBKBRT/TijdvakRelatie/einddatumRelatie']):
            return

        buurt_id = self.foreign_key_id(models.Buurt, r['BBKBRT/BRT/sleutelVerzendend'])

        if not buurt_id:
            log.warning('bouw voor bouwblok niet gevonden: %s' % r['Bouwbloknummer'])
            return

        self.set_pk(models.Bouwblok.__name__, r['Bouwbloknummer'], r['sleutelVerzendend'])

        self.create(models.Bouwblok(
            pk=r['sleutelVerzendend'],
            code=r['Bouwbloknummer'],
            buurt_id=buurt_id
        ))


class ImportWplTask(uva2.AbstractUvaTask):
    name = "import WPL"
    code = "WPL"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'WPLGME'):
            return

        self.create(models.Woonplaats(
            pk=r['sleutelverzendend'],
            code=r['Woonplaatsidentificatie'],
            naam=r['Woonplaatsnaam'],
            document_nummer=r['DocumentnummerMutatieWoonplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieWoonplaats']),
            naam_ptt=r['WoonplaatsPTTSchrijfwijze'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente_id=self.foreign_key_id(models.Gemeente, r['WPLGME/GME/sleutelVerzendend']),
        ))


class ImportOprTask(uva2.AbstractUvaTask):
    name = "import OPR"
    code = "OPR"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'OPRBRN', 'OPRSTS', 'OPRWPL'):
            return

        self.create(models.OpenbareRuimte(
            pk=r['sleutelVerzendend'],
            type=r['TypeOpenbareRuimteDomein'],
            naam=r['NaamOpenbareRuimte'],
            code=r['Straatcode'],
            document_nummer=r['DocumentnummerMutatieOpenbareRuimte'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieOpenbareRuimte']),
            straat_nummer=r['Straatnummer'],
            naam_nen=r['StraatnaamNENSchrijfwijze'],
            naam_ptt=r['StraatnaamPTTSchrijfwijze'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron_id=self.foreign_key_id(models.Bron, r['OPRBRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['OPRSTS/STS/Code']),
            woonplaats_id=self.foreign_key_id(models.Woonplaats, r['OPRWPL/WPL/sleutelVerzendend']),
        ))


class ImportNumTask(uva2.AbstractUvaTask):
    name = "import NUM"
    code = "NUM"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMBRN', 'NUMSTS', 'NUMOPR'):
            return

        self.create(models.Nummeraanduiding(
            pk=r['sleutelVerzendend'],
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
            bron_id=self.foreign_key_id(models.Bron, r['NUMBRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['NUMSTS/STS/Code']),
            openbare_ruimte_id=self.foreign_key_id(models.OpenbareRuimte, r['NUMOPR/OPR/sleutelVerzendend']),
        ))


class ImportLigTask(uva2.AbstractUvaTask):
    name = "import LIG"
    code = "LIG"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'LIGBRN', 'LIGSTS', 'LIGBRT'):
            return

        self.create(models.Ligplaats(
            pk=r['sleutelverzendend'],
            identificatie=r['Ligplaatsidentificatie'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieLigplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieLigplaats']),
            bron_id=self.foreign_key_id(models.Bron, r['LIGBRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['LIGSTS/STS/Code']),
            buurt_id=self.foreign_key_id(models.Buurt, r['LIGBRT/BRT/sleutelVerzendend'])
        ))


class ImportNumLigHfdTask(uva2.AbstractUvaTask):
    name = "import NUMLIGHFD"
    code = "NUMLIGHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMLIGHFD'):
            return

        l_id = self.foreign_key_id(models.Ligplaats, r['NUMLIGHFD/LIG/sleutelVerzendend'])
        if not l_id:
            log.warning("Onbekende ligplaats: %s", r['NUMLIGHFD/LIG/sleutelVerzendend'])
            return

        self.merge_existing(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'], dict(
            ligplaats_id=l_id,
            hoofdadres=True,
        ))


class ImportStaTask(uva2.AbstractUvaTask):
    name = "import STA"
    code = "STA"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'STABRN', 'STASTS', 'STABRT'):
            return

        self.create(models.Standplaats(
            pk=r['sleutelverzendend'],
            identificatie=r['Standplaatsidentificatie'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieStandplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieStandplaats']),
            bron_id=self.foreign_key_id(models.Bron, r['STABRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['STASTS/STS/Code']),
            buurt_id=self.foreign_key_id(models.Buurt, r['STABRT/BRT/sleutelVerzendend'])
        ))


class ImportNumStaHfdTask(uva2.AbstractUvaTask):
    name = "import NUMSTAHFD"
    code = "NUMSTAHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMSTAHFD'):
            return

        s_id = self.foreign_key_id(models.Standplaats, r['NUMSTAHFD/STA/sleutelVerzendend'])
        if not s_id:
            log.warning("Onbekende standplaats: %s", r['NUMSTAHFD/STA/sleutelVerzendend'])
            return

        self.merge_existing(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'], dict(
            standplaats_id=s_id,
            hoofdadres=True,
        ))


class ImportVboTask(uva2.AbstractUvaTask):
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

        self.create(models.Verblijfsobject(
            pk=r['sleutelverzendend'],
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
            reden_afvoer_id=self.foreign_key_id(models.RedenAfvoer, r['VBOAVR/AVR/Code']),
            bron_id=self.foreign_key_id(models.Bron, r['VBOBRN/BRN/Code']),
            eigendomsverhouding_id=self.foreign_key_id(models.Eigendomsverhouding, r['VBOEGM/EGM/Code']),
            financieringswijze_id=self.foreign_key_id(models.Financieringswijze, r['VBOFNG/FNG/Code']),
            gebruik_id=self.foreign_key_id(models.Gebruik, r['VBOGBK/GBK/Code']),
            locatie_ingang_id=self.foreign_key_id(models.LocatieIngang, r['VBOLOC/LOC/Code']),
            ligging_id=self.foreign_key_id(models.Ligging, r['VBOLGG/LGG/Code']),
            # ?=(r['VBOMNT/MNT/Code']),
            toegang_id=self.foreign_key_id(models.Toegang, r['VBOTGG/TGG/Code']),
            # ?=(r['VBOOVR/OVR/Code']),
            status_id=self.foreign_key_id(models.Status, r['VBOSTS/STS/Code']),
            buurt_id=self.foreign_key_id(models.Buurt, r['VBOBRT/BRT/sleutelVerzendend']),
        ))


class ImportNumVboHfdTask(uva2.AbstractUvaTask):
    name = "import NUMVBOHFD"
    code = "NUMVBOHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBOHFD'):
            return

        v_id = self.foreign_key_id(models.Verblijfsobject, r['NUMVBOHFD/VBO/sleutelVerzendend'])
        if not v_id:
            log.warning("Onbekend verblijfsobject: %s", r['NUMVBOHFD/VBO/sleutelVerzendend'])
            return

        self.merge_existing(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'], dict(
            verblijfsobject_id=v_id,
            hoofdadres=True,
        ))


class ImportNumVboNvnTask(uva2.AbstractUvaTask):
    name = "import NUMVBONVN"
    code = "NUMVBONVN"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBONVN'):
            return

        nummeraanduiding_id = r["sleutelVerzendend"]
        verblijfsobject_id = self.foreign_key_id(models.Verblijfsobject, r["NUMVBONVN/sleutelVerzendend"])

        if not verblijfsobject_id:
            log.warning("Onbekend verblijfsobject: %s", r["NUMVBONVN/sleutelVerzendend"])
            return

        self.merge_existing(models.Nummeraanduiding, nummeraanduiding_id, dict(
            verblijfsobject_id=verblijfsobject_id,
            hoofdadres=False,
        ))


class ImportPndTask(uva2.AbstractUvaTask):
    name = "import PND"
    code = "PND"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDSTS', 'PNDBBK'):
            return

        self.create(models.Pand(
            pk=r['sleutelverzendend'],
            identificatie=(r['Pandidentificatie']),
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatiePand']),
            document_nummer=(r['DocumentnummerMutatiePand']),
            bouwjaar=uva2.uva_nummer(r['OorspronkelijkBouwjaarPand']),
            laagste_bouwlaag=uva2.uva_nummer(r['LaagsteBouwlaag']),
            hoogste_bouwlaag=uva2.uva_nummer(r['HoogsteBouwlaag']),
            pandnummer=(r['Pandnummer']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            status_id=self.foreign_key_id(models.Status, r['PNDSTS/STS/Code']),
        ))


class ImportPndVboTask(uva2.AbstractUvaTask):
    name = "import PNDVBO"
    code = "PNDVBO"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDVBO'):
            return

        vbo_id = r['PNDVBO/VBO/sleutelVerzendend']
        vbo = self.get(models.Verblijfsobject, vbo_id)

        if not vbo:
            log.warning("Unknown verblijfsobject: %s", vbo_id)
            return

        pand_id = r['sleutelverzendend']
        pand = self.get(models.Pand, pand_id)

        if not pand:
            log.warning("Unknown pand: %s", pand_id)
            return

        self.create(models.VerblijfsobjectPandRelatie(verblijfsobject=vbo, pand=pand))


class AbstractWktTask(cache.AbstractCacheBasedTask):
    """
    Basic task for processing WKT files
    """

    source_file = None

    def __init__(self, source_path, cache):
        super().__init__(cache)
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter='|')
            for row in rows:
                self.process_row(row[0], GEOSGeometry(row[1]))

    def process_row(self, row_id, geom):
        raise NotImplementedError()


class ImportStaGeoTask(AbstractWktTask):
    name = "import STA WKT"
    source_file = "BAG_STANDPLAATS_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        self.merge_existing(models.Standplaats, '0' + row_id, dict(
            geometrie=geom,
        ))


class ImportLigGeoTask(AbstractWktTask):
    name = "import LIG WKT"
    source_file = "BAG_LIGPLAATS_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        self.merge_existing(models.Ligplaats, '0' + row_id, dict(
            geometrie=geom
        ))


class ImportPndGeoTask(AbstractWktTask):
    name = "import PND WKT"
    source_file = "BAG_PAND_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        self.merge_existing(models.Pand, '0' + row_id, dict(
            geometrie=geom
        ))


class RecreateIndexTask(index.RecreateIndexTask):
    index = 'bag'
    doc_types = [documents.Ligplaats, documents.Standplaats, documents.Verblijfsobject, documents.OpenbareRuimte]


class IndexLigplaatsTask(index.ImportIndexTask):
    name = "index ligplaatsen"
    queryset = models.Ligplaats.objects.prefetch_related('adressen')

    def convert(self, obj):
        return documents.from_ligplaats(obj)


class IndexStandplaatsTask(index.ImportIndexTask):
    name = "index standplaatsen"
    queryset = models.Standplaats.objects.prefetch_related('adressen')

    def convert(self, obj):
        return documents.from_standplaats(obj)


class IndexVerblijfsobjectTask(index.ImportIndexTask):
    name = "index verblijfsobjecten"
    queryset = models.Verblijfsobject.objects.prefetch_related('adressen')

    def convert(self, obj):
        return documents.from_verblijfsobject(obj)


class IndexOpenbareRuimteTask(index.ImportIndexTask):
    name = "index openbare ruimtes"
    queryset = models.OpenbareRuimte.objects

    def convert(self, obj):
        return documents.from_openbare_ruimte(obj)


# geo data gebieden
class AbstractShpTask(mixins.GeoMultiPolygonMixin, GeoModelCodePkMappingMixin, cache.AbstractCacheBasedTask):
    """
    Abstract task for processing shp files
    """

    source_file = None
    model = None
    objects = []
    lookup_field_feat = 'CODE'

    def __init__(self, source_path, cache):
        super().__init__(cache)
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        ds = DataSource(self.source)
        lyr = ds[0]
        [self.process_feature(feat) for feat in lyr]

    def process_feature(self, feat):
        pk = self.get_pk(self.model.__name__, feat.get(self.lookup_field_feat))
        if not pk:
            log.warning('could not find "%s" for model: %s' % (feat.get(self.lookup_field_feat), self.model.__name__))
            return

        self.merge_existing(self.model, pk, dict(
            geometrie=self.get_multipoly(feat.geom.wkt),
        ))

    class Meta:
        __class__ = ABCMeta


class ImportSdlGeoTask(AbstractShpTask):
    """
    layer.fields:

    ['ID', 'NAAM', 'CODE', 'VOLLCODE', 'DOCNR', 'DOCDATUM', 'INGSDATUM', 'EINDDATUM']
    """

    name = "import GBD SDL"
    source_file = "GBD_Stadsdeel.shp"
    model = models.Stadsdeel


class ImportBrtGeoTask(AbstractShpTask):
    """
    layer.fields:

    ['ID', 'NAAM', 'CODE', 'VOLLCODE', 'DOCNR', 'DOCDATUM', 'INGSDATUM', 'EINDDATUM']
    """

    name = "import GBD BRT"
    source_file = "GBD_Buurt.shp"
    model = models.Buurt


class ImportBbkGeoTask(AbstractShpTask):
    """
    layer.fields:

    ['ID', 'CODE', 'DOCNR', 'DOCDATUM', 'INGSDATUM', 'EINDDATUM']
    """

    name = "import GBD BBK"
    source_file = "GBD_Bouwblok.shp"
    model = models.Bouwblok


class ImportBagJob(object):
    name = "Import BAG"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.bag = os.path.join(diva, 'bag')
        self.bag_wkt = os.path.join(diva, 'bag_wkt')
        self.gebieden = os.path.join(diva, 'gebieden')
        self.gebieden_shp = os.path.join(diva, 'gebieden_shp')
        self.cache = cache.Cache()

    def tasks(self):
        return [
            ImportAvrTask(self.bag, self.cache),
            ImportBrnTask(self.bag, self.cache),
            ImportEgmTask(self.bag, self.cache),
            ImportFngTask(self.bag, self.cache),
            ImportGbkTask(self.bag, self.cache),
            ImportLggTask(self.bag, self.cache),
            ImportLocTask(self.bag, self.cache),
            ImportTggTask(self.bag, self.cache),
            ImportStsTask(self.bag, self.cache),

            ImportGmeTask(self.gebieden, self.cache),
            ImportWplTask(self.bag, self.cache),
            ImportSdlTask(self.gebieden, self.cache),
            ImportBrtTask(self.gebieden, self.cache),
            ImportBbkTask(self.gebieden, self.cache),
            ImportOprTask(self.bag, self.cache),

            ImportLigTask(self.bag, self.cache),
            ImportLigGeoTask(self.bag_wkt, self.cache),

            ImportStaTask(self.bag, self.cache),
            ImportStaGeoTask(self.bag_wkt, self.cache),

            ImportVboTask(self.bag, self.cache),

            ImportNumTask(self.bag, self.cache),
            ImportNumLigHfdTask(self.bag, self.cache),
            ImportNumStaHfdTask(self.bag, self.cache),
            ImportNumVboHfdTask(self.bag, self.cache),
            ImportNumVboNvnTask(self.bag, self.cache),

            ImportPndTask(self.bag, self.cache),
            ImportPndGeoTask(self.bag_wkt, self.cache),
            ImportPndVboTask(self.bag, self.cache),

            ImportSdlGeoTask(self.gebieden_shp, self.cache),
            ImportBrtGeoTask(self.gebieden_shp, self.cache),
            ImportBbkGeoTask(self.gebieden_shp, self.cache),

            cache.FlushCacheTask(self.cache),
        ]


class IndexJob(object):
    name = "Update search-index BAG"

    def tasks(self):
        return [
            RecreateIndexTask(),
            IndexOpenbareRuimteTask(),
            IndexLigplaatsTask(),
            IndexStandplaatsTask(),
            IndexVerblijfsobjectTask(),
        ]
