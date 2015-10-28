import hashlib
import logging
import os
import uuid

from django.conf import settings

from django.contrib.gis.geos import Point

from batch import batch
from datasets.generic import uva2, cache, kadaster, index, database
from datasets.bag import models as bag
from . import models, documents

log = logging.getLogger(__name__)


class ImportKotTask(batch.BasicTask):
    name = "Import KOT"

    def __init__(self, path):
        self.path = path
        self.cultuur = dict()
        self.bebouwing = dict()

    def before(self):
        database.clear_models(models.KadastraalObject)

    def after(self):
        self.cultuur.clear()
        self.bebouwing.clear()

    def process(self):
        kadastrale_objecten = uva2.process_uva2(self.path, "KOT", self.process_row)
        models.KadastraalObject.objects.bulk_create(kadastrale_objecten, batch_size=database.BATCH_SIZE)

    def get_soort_cultuur_onbebouwd(self, r):
        scod_code = r['SoortCultuurOnbebouwdDomein']
        if not scod_code:
            return None

        scod = self.cultuur.get(scod_code)
        if scod:
            return scod

        scod = models.SoortCultuurOnbebouwd(
            code=scod_code,
            omschrijving=r['OmschrijvingSoortCultuurOnbebouwdDomein']
        )

        # no bulk create because there are only a few instances, and this would make the code more complex
        scod.save()
        self.cultuur[scod_code] = scod
        return scod

    def get_bebouwingscode(self, r):
        bd_code = r['BebouwingscodeDomein']
        if not bd_code:
            return None

        bd = self.bebouwing.get(bd_code)
        if bd:
            return bd

        bd = models.Bebouwingscode(
            code=bd_code,
            omschrijving=r['OmschrijvingBebouwingscodeDomein']
        )

        # no bulk create because there are only a few Bebouwingscodes, and this would make the code more complex
        bd.save()
        self.bebouwing[bd_code] = bd
        return bd

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        scod = self.get_soort_cultuur_onbebouwd(r)
        bd = self.get_bebouwingscode(r)

        gemeente = r['KadastraleGemeentecodeDomein']
        sectie = r['Sectie']
        perceel = uva2.uva_nummer(r['Perceelnummer'])
        letter = r['ObjectindexletterDomein']
        nummer = uva2.uva_nummer(r['Objectindexnummer'])
        aanduiding = kadaster.get_aanduiding(gemeente, sectie, perceel, letter, nummer)

        x = r['X-Coordinaat']
        y = r['Y-Coordinaat']
        if x and y:
            geo = Point(int(x), int(y))
        else:
            geo = None

        return models.KadastraalObject(
            id=aanduiding,
            gemeentecode=gemeente,
            sectie=sectie,
            perceelnummer=perceel,
            objectindex_letter=letter,
            objectindex_nummer=nummer,
            grootte=uva2.uva_nummer(r['Grootte']),
            grootte_geschat=uva2.uva_indicatie(r['IndicatieGrootteGeschat']),
            cultuur_tekst=r['CultuurTekst'],
            soort_cultuur_onbebouwd=scod,
            meer_culturen_onbebouwd=uva2.uva_indicatie(r['IndicatieMeerCulturenOnbebouwd']),
            bebouwingscode=bd,
            kaartblad=uva2.uva_nummer(r['Kaartblad']),
            ruitletter=r['Ruitletter'],
            ruitnummer=uva2.uva_nummer(r['Ruitnummer']),
            omschrijving_deelperceel=r['OmschrijvingDeelperceel'],
            geometrie=geo,
        )


class ImportKstTask(batch.BasicTask):
    name = "Import KST"

    def __init__(self, path):
        self.path = path

        self.adressen = dict()
        self.titels = dict()
        self.nnps = dict()
        self.landen = dict()

    def before(self):
        database.clear_models(models.KadastraalSubject, models.Land, models.Adres, models.Titel,
                              models.NietNatuurlijkePersoon)

    def after(self):
        self.adressen.clear()
        self.titels.clear()
        self.nnps.clear()
        self.landen.clear()

    def process(self):
        ksts = uva2.process_uva2(self.path, "KST", self.process_row)

        models.Land.objects.bulk_create(self.landen.values(), batch_size=database.BATCH_SIZE)
        models.Adres.objects.bulk_create(self.adressen.values(), batch_size=database.BATCH_SIZE)
        models.Titel.objects.bulk_create(self.titels.values(), batch_size=database.BATCH_SIZE)
        models.NietNatuurlijkePersoon.objects.bulk_create(self.nnps.values(), batch_size=database.BATCH_SIZE)
        models.KadastraalSubject.objects.bulk_create(ksts, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        geslacht = r['GeslachtsaanduidingDomein']
        if geslacht:
            geslacht = geslacht.lower()

        soort = r['SoortSubjectDomein']
        if soort:
            soort = soort.lower()

        woonadres = self.get_adres(r, 'Woonadres')
        woonadres_id = woonadres.id if woonadres else None

        postadres = self.get_adres(r, 'Postadres')
        postadres_id = postadres.id if postadres else None

        return models.KadastraalSubject(
            id=r['sleutelVerzendend'],
            subjectnummer=r['Subjectnummer'],
            titel_of_predikaat=self.get_titel_of_predikaat(r),
            geslachtsaanduiding=geslacht,
            geslachtsnaam=r['Geslachtsnaam'],
            diacritisch=uva2.uva_indicatie(r['IndicatieDiacritisch']),
            naam_niet_natuurlijke_persoon=r['NaamNietNatuurlijkePersoon'],
            soort_subject=soort,
            soort_niet_natuurlijke_persoon=self.get_soort_niet_natuurlijke_persoon(r),
            voorletters=r['Voorletters'],
            voornamen=r['Voornamen'],
            voorvoegsel=r['Voorvoegsel'],
            geboortedatum=uva2.uva_datum(r['Geboortedatum']),
            geboorteplaats=r['Geboorteplaats'],
            overleden=uva2.uva_indicatie(r['IndicatieOverleden']),
            overlijdensdatum=uva2.uva_datum(r['Overlijdensdatum']),
            zetel=r['Zetel'],
            woonadres_id=woonadres_id,
            postadres_id=postadres_id,
            a_nummer=uva2.uva_nummer(r['A-nummer']),
        )

    def get_titel_of_predikaat(self, r):
        top_code = r['AdellijkeTitelOfPredikaatDomein']
        if not top_code:
            return None

        return self.titels.setdefault(top_code, models.Titel(
            code=top_code,
            omschrijving=r['OmschrijvingAdellijkeTitelOfPredikaatDomein']
        ))

    def get_soort_niet_natuurlijke_persoon(self, r):
        soort_code = r['SoortNietNatuurlijkePersoonDomein']
        if not soort_code:
            return None

        return self.nnps.setdefault(soort_code, models.NietNatuurlijkePersoon(
            code=soort_code,
            omschrijving=r['OmschrijvingSoortNietNatuurlijkePersoonDomein'],
        ))

    def get_adres(self, r, adres_type):
        aanduiding = r['AanduidingBijHuisnummer{}'.format(adres_type)]
        adresregel_1 = r['Buitenlands{}regel-1'.format(adres_type)]
        adresregel_2 = r['Buitenlands{}regel-2'.format(adres_type)]
        adresregel_3 = r['Buitenlands{}regel-3'.format(adres_type)]
        huisletter = r['Huisletter{}'.format(adres_type)]
        huisnummer = uva2.uva_nummer(r['Huisnummer{}'.format(adres_type)])
        toevoeging = r['Huisnummertoevoeging{}'.format(adres_type)]
        land_code = r['Landcode{}Domein'.format(adres_type)]
        land_omschrijving = r['OmschrijvingLandcode{}Domein'.format(adres_type)]
        locatie_beschrijving = r['Locatiebeschrijving{}'.format(adres_type)]
        postcode = r['Postcode{}'.format(adres_type)]
        straatnaam = r['Straatnaam{}'.format(adres_type)]
        woonplaats = r['Woonplaats{}'.format(adres_type)]

        values = [aanduiding, adresregel_1, adresregel_2, adresregel_3, huisletter, huisnummer, toevoeging, land_code,
                  locatie_beschrijving, postcode, straatnaam, woonplaats]

        if not any(values):
            return None

        land = self.get_land(land_code, land_omschrijving)

        m = hashlib.md5()
        for v in values:
            m.update(str(v).encode('utf-8'))
        adres_id = m.hexdigest()

        return self.adressen.setdefault(adres_id, models.Adres(
            id=adres_id,
            aanduiding=aanduiding,
            adresregel_1=adresregel_1,
            adresregel_2=adresregel_2,
            adresregel_3=adresregel_3,
            huisletter=huisletter,
            huisnummer=huisnummer,
            toevoeging=toevoeging,
            land=land,
            beschrijving=locatie_beschrijving,
            postcode=postcode,
            straatnaam=straatnaam,
            woonplaats=woonplaats,
        ))

    def get_land(self, land_code, land_omschrijving):
        if not land_code:
            return None

        return self.landen.setdefault(land_code, models.Land(code=land_code, omschrijving=land_omschrijving))


class ImportTteTask(batch.BasicTask):
    name = "Import TTE"

    def __init__(self, path):
        self.path = path
        self.stukken = dict()

    def before(self):
        database.clear_models(models.Transactie, models.SoortStuk)

    def after(self):
        self.stukken.clear()

    def process(self):
        transacties = uva2.process_uva2(self.path, "TTE", self.process_row)

        models.SoortStuk.objects.bulk_create(self.stukken.values(), batch_size=database.BATCH_SIZE)
        models.Transactie.objects.bulk_create(transacties, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, "TTEKSTABR", "TTEKSTBPE"):
            return

        soort = self.get_soort_stuk(r['SoortStukDomein'], r['OmschrijvingSoortStukDomein'])

        return models.Transactie(
            id=r['sleutelVerzendend'],
            registercode=r['RegistercodeDomein'],
            stukdeel_1=r['Stukdeel1'],
            stukdeel_2=r['Stukdeel2'],
            stukdeel_3=r['Stukdeel3'],
            soort_stuk=soort,
            ontvangstdatum=uva2.uva_datum(r['OntvangstdatumStuk']),
            verlijdensdatum=uva2.uva_datum(r['Verlijdensdatum']),
            meer_kadastrale_objecten=uva2.uva_indicatie(r['IndicatieMeerKadastraleObjecten']),
            koopjaar=uva2.uva_nummer(r['Koopjaar']),
            koopsom=uva2.uva_nummer(r['Koopsom']),
            belastingplichtige=uva2.uva_indicatie(r['IndicatieBelastingplichtige']),
        )

    def get_soort_stuk(self, code, omschrijving):
        if not code:
            return None

        return self.stukken.setdefault(code, models.SoortStuk(code=code, omschrijving=omschrijving))


class ImportZrtTask(batch.BasicTask):
    name = "Import ZRT"

    def __init__(self, path):
        self.path = path
        self.soorten_recht = dict()
        self.kot_ids = set()
        self.kst_ids = set()
        self.tte_ids = set()

    def before(self):
        database.clear_models(models.ZakelijkRecht, models.SoortRecht)
        self.kot_ids = set(models.KadastraalObject.objects.values_list("id", flat=True))
        self.kst_ids = set(models.KadastraalSubject.objects.values_list("id", flat=True))
        self.tte_ids = set(models.Transactie.objects.values_list("id", flat=True))

    def after(self):
        self.soorten_recht.clear()
        self.kot_ids.clear()
        self.kst_ids.clear()
        self.tte_ids.clear()

    def process(self):
        zrts = uva2.process_uva2(self.path, "ZRT", self.process_row)

        models.SoortRecht.objects.bulk_create(self.soorten_recht.values(), batch_size=database.BATCH_SIZE)
        models.ZakelijkRecht.objects.bulk_create(zrts, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, "ZRTKOT", "ZRTKST", "ZRTTTE"):
            return

        soort = self.get_soort_recht(r['SoortRechtDomein'], r['OmschrijvingSoortRechtDomein'])

        pk = r['sleutelVerzendend']
        kot_id = kadaster.get_aanduiding(
            r['ZRTKOT/KOT/KadastraleGemeentecodeDomein'],
            r['ZRTKOT/KOT/Sectie'],
            r['ZRTKOT/KOT/Perceelnummer'],
            r['ZRTKOT/KOT/ObjectindexletterDomein'],
            r['ZRTKOT/KOT/Objectindexnummer']
        )
        kst_id = r['ZRTKST/KST/sleutelVerzendend']
        tte_id = r['ZRTTTE/TTE/sleutelVerzendend']

        if kot_id not in self.kot_ids:
            log.warn("ZakelijkRecht {} references non-existing KOT {}; skipping".format(pk, kot_id))
            return

        if kst_id not in self.kst_ids:
            log.warn("ZakelijkRecht {} references non-existing KST {}; skipping".format(pk, kst_id))
            return

        if tte_id not in self.tte_ids:
            log.warn("ZakelijkRecht {} references non-existing TTE {}; skipping".format(pk, tte_id))
            return

        return models.ZakelijkRecht(
            id=pk,
            identificatie=r['ZakelijkRechtidentificatie'],
            soort_recht=soort,
            volgnummer=uva2.uva_nummer(r['ZakelijkRechtVolgnummer']),
            aandeel_medegerechtigden=r['AandeelVanMedegerechtigdengroepInRecht'],
            aandeel_subject=r['AandeelVanSubjectInRecht'],
            einde_filiatie=uva2.uva_indicatie(r['IndicatieEindeFiliatie']),
            sluimerend=uva2.uva_indicatie(r['IndicatieSluimerend']),
            kadastraal_object_id=kot_id,
            kadastraal_subject_id=kst_id,
            transactie_id=tte_id,
        )

    def get_soort_recht(self, code, omschrijving):
        if not code:
            return None

        return self.soorten_recht.setdefault(code, models.SoortRecht(code=code, omschrijving=omschrijving))


class ImportKotVboTask(batch.BasicTask):
    name = "Import KOTVBO"

    def __init__(self, path):
        self.path = path
        self.vbo_ids = set()
        self.kot_ids = set()

    def before(self):
        # database.clear_models(models.KadastraalObjectVerblijfsobject)
        if not self.vbo_ids:
            self.vbo_ids = set(bag.Verblijfsobject.objects.values_list('id', flat=True))

        self.kot_ids = set(models.KadastraalObject.objects.values_list('id', flat=True))

    def after(self):
        self.vbo_ids.clear()
        self.kot_ids.clear()

    def process(self):
        kovs = uva2.process_uva2(self.path, "KOTVBO", self.process_row)
        models.KadastraalObjectVerblijfsobject.objects.bulk_create(kovs, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relatie(r, "KOTVBO"):
            return

        pk = r['sleutelverzendend']
        vbo_id = r['KOTVBO/VBO/Verblijfsobjectidentificatie']
        kot_id = kadaster.get_aanduiding(
            r['KadastraleGemeentecodeDomein'],
            r['Sectie'],
            r['Perceelnummer'],
            r['ObjectindexletterDomein'],
            r['Objectindexnummer'],
        )

        if vbo_id not in self.vbo_ids:
            log.warn("KOTVBO {} references non-existing verblijfsobject {}; skipping".format(pk, vbo_id))
            return

        if kot_id not in self.kot_ids:
            log.warn("KOTVBO {} references non-existing kadastraal object {}; skipping".format(pk, kot_id))
            return

        return models.KadastraalObjectVerblijfsobject(
            id=uuid.uuid4(),
            kadastraal_object_id=kot_id,
            verblijfsobject_id=vbo_id,
        )


class ImportKadasterJob(object):
    name = "Import Kadaster - AKR"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.akr = os.path.join(diva, 'kadaster', 'akr')
        self.cache = cache.Cache()

    def tasks(self):
        return [
            # ImportKotTask(self.akr),
            ImportKstTask(self.akr),
            ImportTteTask(self.akr),
            ImportZrtTask(self.akr),
            ImportKotVboTask(self.akr),
        ]


class RecreateIndexTask(index.RecreateIndexTask):
    index = 'brk'
    doc_types = [documents.KadastraalObject, documents.KadastraalSubject]


class IndexSubjectTask(index.ImportIndexTask):
    name = "index kadastraal subject"
    queryset = models.KadastraalSubject.objects

    def convert(self, obj):
        return documents.from_kadastraal_subject(obj)


class IndexObjectTask(index.ImportIndexTask):
    name = "index kadastraal object"
    queryset = models.KadastraalObject.objects

    def convert(self, obj):
        return documents.from_kadastraal_object(obj)


class IndexKadasterJob(object):
    name = "Update search-index BRK"

    def tasks(self):
        return [
            RecreateIndexTask(),
            IndexSubjectTask(),
            IndexObjectTask(),
        ]
