from collections import OrderedDict
import csv
import logging
import os

from django.contrib.gis.geos import Point, GEOSGeometry

from atlas import models
from atlas_jobs import uva2

log = logging.getLogger(__name__)


class Cache(object):
    """
    In-memory cache for all bag-data.
    """

    def __init__(self):
        self.cache = OrderedDict()

    def clear(self):
        """
        Clears the cache.
        """
        self.cache.clear()

    def put(self, obj):
        """
        Adds an object to the cache.
        """
        model = type(obj)
        pk = obj.pk
        self.cache.setdefault(model, dict())[pk] = obj

    def models(self):
        """
        Returns all the models that have been added to the cache in the order in which they were first added.
        """
        return list(self.cache.keys())

    def objects(self, model):
        """
        Returns all objects stored for a specific model.
        """
        return list(self.cache[model].values())

    def get(self, model, pk):
        """
        Returns the object with the specified PK, or None
        """
        return self.cache.get(model, dict()).get(pk)


bag_cache = Cache()


class AbstractCacheBasedTask(object):
    def execute(self):
        raise NotImplementedError()

    def create(self, obj):
        bag_cache.put(obj)

    def foreign_key_id(self, model, model_id):
        obj = bag_cache.get(model, model_id)
        if not obj:
            return None

        return obj.pk

    def get(self, model, pk):
        return bag_cache.get(model, pk)

    def merge_existing(self, model, pk, values):
        obj = bag_cache.get(model, pk)
        if not obj:
            return

        for key, value in values.items():
            setattr(obj, key, value)

        bag_cache.put(obj)


class FlushCacheTask(object):
    """
     1. Remove all data from the database
     2. Use batch-insert to insert all data into the database
     3. Clear the cache
    """
    name = "Flush data to database"
    chunk_size = 500

    def execute(self):
        global bag_cache
        stored_models = bag_cache.models()

        # drop all data
        for model in reversed(stored_models):
            log.info("Dropping data from %s", model)
            model.objects.all().delete()

        # batch-insert all data
        for model in stored_models:
            log.info("Creating data for %s", model)
            values = bag_cache.objects(model)

            for i in range(0, len(values), self.chunk_size):
                model.objects.bulk_create(values[i:i + self.chunk_size])

        # clear cache
        bag_cache.clear()


class AbstractUvaTask(AbstractCacheBasedTask):
    """
    Basic task for processing UVA2 files
    """
    code = None

    def __init__(self, source):
        super().__init__()
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


class ImportGmeTask(AbstractUvaTask):
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

        self.create(models.Stadsdeel(
            pk=(r['sleutelVerzendend']),
            code=r['Stadsdeelcode'],
            naam=r['Stadsdeelnaam'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente_id=(self.foreign_key_id(models.Gemeente, r['SDLGME/GME/sleutelVerzendend'])),
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

        self.create(models.Buurt(
            pk=r['sleutelVerzendend'],
            code=r['Buurtcode'],
            naam=r['Buurtnaam'],
            stadsdeel_id=self.foreign_key_id(models.Stadsdeel, r['BRTSDL/SDL/sleutelVerzendend']),
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


class ImportOprTask(AbstractUvaTask):
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


class ImportNumTask(AbstractUvaTask):
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


class ImportLigTask(AbstractUvaTask):
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


class ImportNumLigHfdTask(AbstractUvaTask):
    name = "import NUMLIGHFD"
    code = "NUMLIGHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMLIGHFD'):
            return

        self.merge_existing(models.Ligplaats, r['NUMLIGHFD/LIG/sleutelVerzendend'], dict(
            hoofdadres_id=self.foreign_key_id(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportStaTask(AbstractUvaTask):
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


class ImportNumStaHfdTask(AbstractUvaTask):
    name = "import NUMSTAHFD"
    code = "NUMSTAHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMSTAHFD'):
            return

        self.merge_existing(models.Standplaats, r['NUMSTAHFD/STA/sleutelVerzendend'], dict(
            hoofdadres_id=self.foreign_key_id(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
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


class ImportNumVboHfdTask(AbstractUvaTask):
    name = "import NUMVBOHFD"
    code = "NUMVBOHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBOHFD'):
            return

        self.merge_existing(models.Verblijfsobject, r['NUMVBOHFD/VBO/sleutelVerzendend'], dict(
            hoofdadres_id=self.foreign_key_id(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportPndTask(AbstractUvaTask):
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


class ImportPndVboTask(AbstractUvaTask):
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


class AbstractWktTask(AbstractCacheBasedTask):
    """
    Basic task for processing WKT files
    """

    source_file = None

    def __init__(self, source_path):
        super().__init__()
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
