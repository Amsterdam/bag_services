import os
from django.conf import settings
from datasets.generic import uva2, cache

from . import models


class ImportKotTask(uva2.AbstractUvaTask):

    name = "import KOT"
    code = "KOT"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        scod = self.get_soort_cultuur_onbebouwd_domein(r)
        bd = self.get_bebouwingscode_domein(r)

        self.create(models.KadastraalObject(
            id=r['sleutelverzendend'],
            gemeentecode_domein=r['KadastraleGemeentecodeDomein'],
            sectie=r['Sectie'],
            perceelnummer=uva2.uva_nummer(r['Perceelnummer']),
            objectindex_letter=r['ObjectindexletterDomein'],
            objectindex_nummer=uva2.uva_nummer(r['Objectindexnummer']),
            grootte=uva2.uva_nummer(r['Grootte']),
            grootte_geschat=uva2.uva_indicatie(r['IndicatieGrootteGeschat']),
            cultuur_tekst=r['CultuurTekst'],
            soort_cultuur_onbebouwd_domein=scod,
            meer_culturen_onbebouwd=uva2.uva_indicatie(r['IndicatieMeerCulturenOnbebouwd']),
            bebouwingscode_domein=bd,
            kaartblad=uva2.uva_nummer(r['Kaartblad']),
            ruitletter=r['Ruitletter'],
            ruitnummer=uva2.uva_nummer(r['Ruitnummer']),
            omschrijving_deelperceel=r['OmschrijvingDeelperceel'],
        ))

    def get_soort_cultuur_onbebouwd_domein(self, r):
        scod_code = r['SoortCultuurOnbebouwdDomein']
        if not scod_code:
            return None

        scod = self.get(models.SoortCultuurOnbebouwdDomein, scod_code)
        if scod:
            return scod

        scod = models.SoortCultuurOnbebouwdDomein(code=scod_code,
                                                  omschrijving=r['OmschrijvingSoortCultuurOnbebouwdDomein'])
        self.create(scod)
        return scod

    def get_bebouwingscode_domein(self, r):
        bd_code = r['BebouwingscodeDomein']
        if not bd_code:
            return None

        bd = self.get(models.BebouwingscodeDomein, bd_code)
        if bd:
            return bd

        bd = models.BebouwingscodeDomein(code=bd_code,
                                         omschrijving=r['OmschrijvingBebouwingscodeDomein'])
        self.create(bd)
        return bd


class ImportKadasterJob(object):
    name = "atlas-import BKR"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.akr = os.path.join(diva, 'kadaster', 'akr')
        self.cache = cache.Cache()

    def tasks(self):
        return [
            ImportKotTask(self.akr, self.cache),

            cache.FlushCacheTask(self.cache),
        ]