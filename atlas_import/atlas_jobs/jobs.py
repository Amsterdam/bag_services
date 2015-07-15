import logging

from atlas import models
from . import uva2

log = logging.getLogger(__name__)


def merge(model, pk, values):
    obj, created = model.objects.get_or_create(pk=pk, defaults=values)
    if created:
        return

    for attr, value in values.items():
        stored = getattr(obj, attr)
        if stored != value:
            setattr(obj, attr, value)

    obj.save()


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


class ImportBrnTask(RowBasedUvaTask):
    name = "import BRN"
    code = "BRN"

    def process_row(self, r):
        merge(models.Bron, r['Code'], dict(
            omschrijving=r['Omschrijving']
        ))


class ImportStsTask(RowBasedUvaTask):
    name = "import STS"
    code = "STS"

    def process_row(self, r):
        merge(models.Status, r['Code'], dict(
            omschrijving=r['Omschrijving']
        ))


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
            bron=foreign_key(models.Bron, r['LIGBRN/BRN/Code']),
            status=foreign_key(models.Status, r['LIGSTS/STS/Code']),
            buurt=foreign_key(models.Buurt, r['LIGBRT/BRT/sleutelVerzendend'])
        ))


class ImportJob(object):
    name = "atlas-import"

    def __init__(self):
        self.bag = 'atlas_jobs/fixtures/testset/bag'
        self.gebieden = 'atlas_jobs/fixtures/testset/gebieden'

    def tasks(self):
        return [
            ImportBrnTask(self.bag),
            ImportStsTask(self.bag),
            ImportGmeTask(self.gebieden),
            ImportSdlTask(self.gebieden),
            ImportBrtTask(self.gebieden),
            ImportLigTask(self.bag),
        ]
