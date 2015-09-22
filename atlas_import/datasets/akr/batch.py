import hashlib
import logging
import os
import uuid

from django.conf import settings

from datasets.generic import uva2, cache, kadaster
from datasets.bag import models as bag
from . import models

log = logging.getLogger(__name__)


class ImportKotTask(uva2.AbstractUvaTask):
    name = "import KOT"
    code = "KOT"

    def execute(self):
        self.require(models.SoortCultuurOnbebouwd)
        self.require(models.Bebouwingscode)
        super().execute()

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

        self.create(models.KadastraalObject(
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
        ))

    def get_soort_cultuur_onbebouwd(self, r):
        scod_code = r['SoortCultuurOnbebouwdDomein']
        if not scod_code:
            return None

        scod = self.get(models.SoortCultuurOnbebouwd, scod_code)
        if scod:
            return scod

        scod = models.SoortCultuurOnbebouwd(code=scod_code,
                                            omschrijving=r['OmschrijvingSoortCultuurOnbebouwdDomein'])
        self.create(scod)
        return scod

    def get_bebouwingscode(self, r):
        bd_code = r['BebouwingscodeDomein']
        if not bd_code:
            return None

        bd = self.get(models.Bebouwingscode, bd_code)
        if bd:
            return bd

        return self.create(models.Bebouwingscode(code=bd_code,
                                                 omschrijving=r['OmschrijvingBebouwingscodeDomein']))


class ImportKstTask(uva2.AbstractUvaTask):
    name = "import KST"
    code = "KST"

    def execute(self):
        self.require(models.Land)
        self.require(models.Titel)
        self.require(models.NietNatuurlijkePersoon)
        self.require(models.Adres)

        super().execute()

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

        self.create(models.KadastraalSubject(
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
        ))

    def get_titel_of_predikaat(self, r):
        top_code = r['AdellijkeTitelOfPredikaatDomein']
        if not top_code:
            return None

        top = self.get(models.Titel, top_code)
        if top:
            return top

        return self.create(models.Titel(code=top_code,
                                        omschrijving=r['OmschrijvingAdellijkeTitelOfPredikaatDomein']))

    def get_soort_niet_natuurlijke_persoon(self, r):
        soort_code = r['SoortNietNatuurlijkePersoonDomein']
        if not soort_code:
            return None

        soort = self.get(models.NietNatuurlijkePersoon, soort_code)
        if soort:
            return soort

        return self.create(
            models.NietNatuurlijkePersoon(code=soort_code,
                                          omschrijving=r['OmschrijvingSoortNietNatuurlijkePersoonDomein']))

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

        adres = self.get(models.Adres, adres_id)
        if adres:
            return adres

        return self.create(models.Adres(
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

        land = self.get(models.Land, land_code)
        if land:
            return land

        return self.create(models.Land(code=land_code, omschrijving=land_omschrijving))


class ImportTteTask(uva2.AbstractUvaTask):
    name = "import TTE"
    code = "TTE"

    def execute(self):
        self.require(models.SoortStuk)
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, "TTEKSTABR", "TTEKSTBPE"):
            return

        soort = self.get_soort_stuk(r['SoortStukDomein'], r['OmschrijvingSoortStukDomein'])

        self.create(models.Transactie(
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
        ))

    def get_soort_stuk(self, code, omschrijving):
        if not code:
            return None

        soort = self.get(models.SoortStuk, code)
        if soort:
            return soort

        return self.create(models.SoortStuk(code=code, omschrijving=omschrijving))


class ImportZrtTask(uva2.AbstractUvaTask):
    name = "import ZRT"
    code = "ZRT"

    def execute(self):
        self.require(models.SoortRecht)
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, "ZRTKOT", "ZRTKST", "ZRTTTE"):
            return

        soort = self.get_soort_recht(r['SoortRechtDomein'], r['OmschrijvingSoortRechtDomein'])

        aanduiding = kadaster.get_aanduiding(
            r['ZRTKOT/KOT/KadastraleGemeentecodeDomein'],
            r['ZRTKOT/KOT/Sectie'],
            r['ZRTKOT/KOT/Perceelnummer'],
            r['ZRTKOT/KOT/ObjectindexletterDomein'],
            r['ZRTKOT/KOT/Objectindexnummer']
        )

        kot_id = self.foreign_key_id(models.KadastraalObject, aanduiding)
        if not kot_id:
            log.warning("Onbekend object: %s", r['ZRTKOT/KOT/sleutelVerzendend'])
            return

        kst_id = self.foreign_key_id(models.KadastraalSubject, r['ZRTKST/KST/sleutelVerzendend'])
        if not kst_id:
            log.warning("Onbekend subject: %s", r['ZRTKST/KST/sleutelVerzendend'])
            return

        tte_id = self.foreign_key_id(models.Transactie, r['ZRTTTE/TTE/sleutelVerzendend'])
        if not tte_id:
            log.warning("Onbekende transactie: %s", r['ZRTTTE/TTE/sleutelVerzendend'])
            return

        self.create(models.ZakelijkRecht(
            id=r['sleutelVerzendend'],
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
        ))

    def get_soort_recht(self, code, omschrijving):
        if not code:
            return None
        soort = self.get(models.SoortRecht, code)
        if soort:
            return soort

        return self.create(models.SoortRecht(code=code, omschrijving=omschrijving))


class ImportKotVboTask(uva2.AbstractUvaTask):
    name = "import KOTVBO"
    code = "KOTVBO"

    def __init__(self, source, cache):
        super().__init__(source, cache)
        self.valid_vbo_ids = []

    def execute(self):
        if not self.valid_vbo_ids:
            self.valid_vbo_ids = set(bag.Verblijfsobject.objects.values_list('id', flat=True))
        try:
            super().execute()
        finally:
            self.valid_vbo_ids = []

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relatie(r, "KOTVBO"):
            return

        vbo_id = r['KOTVBO/VBO/Verblijfsobjectidentificatie']
        if vbo_id not in self.valid_vbo_ids:
            log.warning("Unknown VBO: {}".format(vbo_id))
            return

        aanduiding = kadaster.get_aanduiding(
            r['KadastraleGemeentecodeDomein'],
            r['Sectie'],
            r['Perceelnummer'],
            r['ObjectindexletterDomein'],
            r['Objectindexnummer'],
        )

        self.create(models.KadastraalObjectVerblijfsobject(
            id=uuid.uuid4(),
            kadastraal_object_id=self.foreign_key_id(models.KadastraalObject, aanduiding),
            verblijfsobject_id=vbo_id,
        ))


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
            ImportKotTask(self.akr, self.cache),
            ImportKstTask(self.akr, self.cache),
            ImportTteTask(self.akr, self.cache),
            ImportZrtTask(self.akr, self.cache),
            ImportKotVboTask(self.akr, self.cache),

            cache.FlushCacheTask(self.cache),
        ]
