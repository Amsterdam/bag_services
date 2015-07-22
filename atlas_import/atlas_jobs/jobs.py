import csv
import logging
import os

from django.contrib.gis.geos import GEOSGeometry

from atlas import models
from . import uva2

log = logging.getLogger(__name__)


def merge(model, pk, values):
    model.objects.update_or_create(pk=pk, defaults=values)


def foreign_key(model, key):
    if not key:
        return None

    try:
        return model.objects.get(pk=key)
    except model.DoesNotExist:
        log.warning("Could not load object of type %s with key %s", model, key)
        return None


class RowBasedUvaTask(object):
    code = None

    def __init__(self, source):
        self.source = uva2.resolve_file(source, self.code)

    def execute(self):
        with uva2.uva_reader(self.source) as rows:
            for r in rows:
                self.process_row(r)

    def process_row(self, r):
        raise NotImplementedError()


class CodeOmschrijvingUvaTask(RowBasedUvaTask):
    model = None

    def process_row(self, r):
        merge(self.model, r['Code'], dict(
            omschrijving=r['Omschrijving']
        ))


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


class ImportGmeTask(RowBasedUvaTask):
    name = "import GME"
    code = "GME"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        merge(models.Gemeente, r['sleutelVerzendend'], dict(
            code=r['Gemeentecode'],
            naam=r['Gemeentenaam'],
            verzorgingsgebied=uva2.uva_indicatie(r['IndicatieVerzorgingsgebied']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class ImportSdlTask(RowBasedUvaTask):
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


class ImportBrtTask(RowBasedUvaTask):
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


class ImportWplTask(RowBasedUvaTask):
    name = "import WPL"
    code = "WPL"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['WPLGME/TijdvakRelatie/begindatumRelatie'],
                               r['WPLGME/TijdvakRelatie/einddatumRelatie']):
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


class ImportOprTask(RowBasedUvaTask):
    name = "import OPR"
    code = "OPR"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['OPRBRN/TijdvakRelatie/begindatumRelatie'],
                               r['OPRBRN/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['OPRSTS/TijdvakRelatie/begindatumRelatie'],
                               r['OPRSTS/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['OPRWPL/TijdvakRelatie/begindatumRelatie'],
                               r['OPRWPL/TijdvakRelatie/einddatumRelatie']):
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


class ImportNumTask(RowBasedUvaTask):
    name = "import NUM"
    code = "NUM"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['NUMBRN/TijdvakRelatie/begindatumRelatie'],
                               r['NUMBRN/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['NUMSTS/TijdvakRelatie/begindatumRelatie'],
                               r['NUMSTS/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['NUMOPR/TijdvakRelatie/begindatumRelatie'],
                               r['NUMOPR/TijdvakRelatie/einddatumRelatie']):
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


class ImportLigTask(RowBasedUvaTask):
    name = "import LIG"
    code = "LIG"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['LIGBRN/TijdvakRelatie/begindatumRelatie'],
                               r['LIGBRN/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['LIGSTS/TijdvakRelatie/begindatumRelatie'],
                               r['LIGSTS/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['LIGBRT/TijdvakRelatie/begindatumRelatie'],
                               r['LIGBRT/TijdvakRelatie/einddatumRelatie']):
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


class ImportNumLigHfdTask(RowBasedUvaTask):
    name = "import NUMLIGHFD"
    code = "NUMLIGHFD"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['NUMLIGHFD/TijdvakRelatie/begindatumRelatie'],
                               r['NUMLIGHFD/TijdvakRelatie/einddatumRelatie']):
            return

        merge(models.Ligplaats, r['NUMLIGHFD/LIG/sleutelVerzendend'], dict(
            hoofdadres=foreign_key(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportLigGeoTask(object):
    name = "import LIG WKT"
    source_file = "BAG_LIGPLAATS_GEOMETRIE.dat"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter='|')
            for row in rows:
                self.process_row(row)

    def process_row(self, row):
        ligplaats_id = '0' + row[0]
        wkt = row[1]

        try:
            l = models.Ligplaats.objects.get(pk=ligplaats_id)
            poly = GEOSGeometry(wkt)

            l.geometrie = poly
            l.save()
        except models.Ligplaats.DoesNotExist:
            log.warn("Could not load Ligplaats with key %s", ligplaats_id)


class ImportStaTask(RowBasedUvaTask):
    name = "import STA"
    code = "STA"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['STABRN/TijdvakRelatie/begindatumRelatie'],
                               r['STABRN/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['STASTS/TijdvakRelatie/begindatumRelatie'],
                               r['STASTS/TijdvakRelatie/einddatumRelatie']):
            return

        if not uva2.uva_geldig(r['STABRT/TijdvakRelatie/begindatumRelatie'],
                               r['STABRT/TijdvakRelatie/einddatumRelatie']):
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


class ImportStaGeoTask(object):
    name = "import STA WKT"
    source_file = "BAG_STANDPLAATS_GEOMETRIE.dat"

    def __init__(self, source_path):
        self.source = os.path.join(source_path, self.source_file)

    def execute(self):
        with open(self.source) as f:
            rows = csv.reader(f, delimiter='|')
            for row in rows:
                self.process_row(row)

    def process_row(self, row):
        standplaats_id = '0' + row[0]
        wkt = row[1]

        try:
            l = models.Standplaats.objects.get(pk=standplaats_id)
            poly = GEOSGeometry(wkt)

            l.geometrie = poly
            l.save()
        except models.Standplaats.DoesNotExist:
            log.warn("Could not load Ligplaats with key %s", standplaats_id)


class ImportNumStaHfdTask(RowBasedUvaTask):
    name = "import NUMSTAHFD"
    code = "NUMSTAHFD"

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['NUMSTAHFD/TijdvakRelatie/begindatumRelatie'],
                               r['NUMSTAHFD/TijdvakRelatie/einddatumRelatie']):
            return

        merge(models.Standplaats, r['NUMSTAHFD/STA/sleutelVerzendend'], dict(
            hoofdadres=foreign_key(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportJob(object):
    name = "atlas-import"

    def __init__(self):
        self.bag = 'atlas_jobs/fixtures/testset/bag'
        self.bag_wkt = 'atlas_jobs/fixtures/testset/bag_wkt'
        self.gebieden = 'atlas_jobs/fixtures/testset/gebieden'

    def tasks(self):
        return [
            ImportBrnTask(self.bag),
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
        ]
