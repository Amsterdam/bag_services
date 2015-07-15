import os

from atlas import models
from . import uva2


def merge(model, pk, values):
    obj, created = model.objects.get_or_create(pk=pk, defaults=values)
    if created:
        return

    for attr, value in values.items():
        stored = getattr(obj, attr)
        if stored != value:
            setattr(obj, attr, value)

    obj.save()


class RowBasedUvaTask(object):
    def __init__(self, source):
        self.source = source

    def execute(self):
        with uva2.uva_reader(self.source) as rows:
            for r in rows:
                self.process_row(r)

    def process_row(self, r):
        raise NotImplementedError()


class ImportBrnTask(RowBasedUvaTask):
    name = "import BRN"

    def process_row(self, r):
        merge(models.Bron, r['Code'], dict(
            omschrijving=r['Omschrijving']
        ))


class ImportStsTask(RowBasedUvaTask):
    name = "import STS"

    def process_row(self, r):
        merge(models.Status, r['Code'], dict(
            omschrijving=r['Omschrijving']
        ))


class ImportGmeTask(RowBasedUvaTask):
    name = "import GMT"

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

        bron = r['LIGBRN/BRN/Code']
        status = r['LIGSTS/STS/Code']
        buurt = r['LIGBRT/BRT/Buurtcode']
        merge(models.Ligplaats, r['sleutelverzendend'], dict(
            identificatie=int(r['Ligplaatsidentificatie']),
            ligplaats_nummer=int(r['LigplaatsnummerGemeente']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron=models.Bron.objects.get(pk=bron) if bron else None,
            status=models.Status.objects.get(pk=status) if status else None,
            # buurt=models.Buurt.objects.get(pk=buurt) if buurt else None,
        ))


class ImportJob(object):
    name = "atlas-import"

    def __init__(self):
        self.base_dir = 'atlas_jobs/fixtures/examplebag'

    def tasks(self):
        return [
            ImportBrnTask(os.path.join(self.base_dir, 'BRN_20071001_J_20000101_20050101.UVA2')),
            ImportStsTask(os.path.join(self.base_dir, 'STS_20071001_J_20000101_20050101.UVA2')),
            ImportGmeTask(os.path.join(self.base_dir, 'GME_20071001_J_20000101_20050101.UVA2')),
            ImportSdlTask(os.path.join(self.base_dir, 'SDL_20071001_J_20000101_20050101.UVA2')),
            ImportBrtTask(os.path.join(self.base_dir, 'BRT_20071001_J_20000101_20050101.UVA2')),
            ImportLigTask(os.path.join(self.base_dir, 'LIG_20071001_J_20000101_20050101.UVA2'))
        ]


