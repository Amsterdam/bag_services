import logging

from batch import batch
from datasets.brk import models
from datasets.generic import geo, database

log = logging.getLogger(__name__)


class ImportGemeenteTask(batch.BasicTask):
    name = "Import Gemeente"

    def __init__(self, path):
        self.path = path

    def before(self):
        database.clear_models(models.Gemeente)

    def after(self):
        pass

    def process(self):
        gemeentes = geo.process_shp(self.path, 'BRK_GEMEENTE.shp', self.process_feature)
        models.Gemeente.objects.bulk_create(gemeentes, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        return models.Gemeente(
            gemeente=feat.get('GEMEENTE'),
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraleGemeenteTask(batch.BasicTask):
    name = "Import Kadastrale Gemeente"

    def __init__(self, path):
        self.path = path
        self.gemeentes = set()

    def before(self):
        database.clear_models(models.KadastraleGemeente)
        self.gemeentes = set(models.Gemeente.objects.values_list('gemeente', flat=True))

    def after(self):
        self.gemeentes.clear()

    def process(self):
        kgs = geo.process_shp(self.path, 'BRK_KAD_GEMEENTE.shp', self.process_feature)
        models.KadastraleGemeente.objects.bulk_create(kgs, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        pk = feat.get('LKI_KADGEM')
        gemeente_id = feat.get('GEMEENTE')

        if gemeente_id not in self.gemeentes:
            log.warn("Kadastrale Gemeente {} references non-existing Gemeente {}; skipping".format(pk, gemeente_id))
            return

        return models.KadastraleGemeente(
            id=pk,
            gemeente_id=gemeente_id,
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraleSectieTask(batch.BasicTask):
    name = "Import Kadastrale Sectie"

    def __init__(self, path):
        self.path = path
        self.gemeentes = set()

    def before(self):
        database.clear_models(models.KadastraleSectie)
        self.gemeentes = set(models.KadastraleGemeente.objects.values_list('pk', flat=True))

    def after(self):
        self.gemeentes.clear()

    def process(self):
        s = geo.process_shp(self.path, 'BRK_KAD_SECTIE.shp', self.process_feature)
        models.KadastraleSectie.objects.bulk_create(s, batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        kad_gem_id = feat.get('LKI_KADGEM')
        sectie = feat.get('LKI_SECTIE')
        pk = "{}{}".format(kad_gem_id, sectie)

        if kad_gem_id not in self.gemeentes:
            log.warn("Kadastrale sectie {} references non-existing Kadastrale Gemeente {}; skipping".format(pk, kad_gem_id))
            return

        return models.KadastraleSectie(
            pk=pk,
            sectie=sectie,
            kadastrale_gemeente_id=kad_gem_id,
            geometrie=geo.get_multipoly(feat.geom.wkt)
        )