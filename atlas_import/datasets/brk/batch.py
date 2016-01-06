import datetime
import hashlib
import logging
import os

from django.conf import settings

from batch import batch
from datasets.bag import models as bag
from datasets.brk import models, documents
from datasets.generic import geo, database, uva2, kadaster, index

log = logging.getLogger(__name__)


def _get_related(code, omschrijving, cache, model):
    if not code or code == 'geenWaarde':
        return None
    cached = cache.get(code)
    if cached:
        return cached

    obj = model.objects.create(
            code=code,
            omschrijving=omschrijving
    )
    cache[code] = obj
    return obj


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
        kgs = dict(geo.process_shp(self.path, 'BRK_KAD_GEMEENTE.shp', self.process_feature))
        models.KadastraleGemeente.objects.bulk_create(kgs.values(), batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        pk = feat.get('KADGEMCODE')
        gemeente_id = feat.get('GEMEENTE')

        if gemeente_id not in self.gemeentes:
            log.warn("Kadastrale Gemeente {} references non-existing Gemeente {}; skipping".format(pk, gemeente_id))
            return

        return pk, models.KadastraleGemeente(
                id=pk,
                naam=feat.get('KADGEM'),
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
        s = dict(geo.process_shp(self.path, 'BRK_KAD_SECTIE.shp', self.process_feature))
        models.KadastraleSectie.objects.bulk_create(s.values(), batch_size=database.BATCH_SIZE)

    def process_feature(self, feat):
        kad_gem_id = feat.get('KADGEMCODE')
        sectie = feat.get('SECTIE')
        pk = "{}{}".format(kad_gem_id, sectie)

        if kad_gem_id not in self.gemeentes:
            log.warn(
                    "Kadastrale sectie {} references non-existing Kadastrale Gemeente {}; skipping".format(pk,
                                                                                                           kad_gem_id))
            return

        return pk, models.KadastraleSectie(
                pk=pk,
                sectie=sectie,
                kadastrale_gemeente_id=kad_gem_id,
                geometrie=geo.get_multipoly(feat.geom.wkt)
        )


class ImportKadastraalSubjectTask(batch.BasicTask):
    name = "Import Kadastraal Subject"

    def __init__(self, path):
        self.path = path
        self.geslacht = dict()
        self.beschikkingsbevoegdheid = dict()
        self.aanduiding_naam = dict()
        self.land = dict()
        self.adressen = dict()
        self.rechtsvorm = dict()

    def before(self):
        database.clear_models(
                models.KadastraalSubject,
                models.Geslacht,
                models.Beschikkingsbevoegdheid,
                models.AanduidingNaam,
                models.Land,
                models.Adres,
                models.Rechtsvorm,
        )

    def after(self):
        self.geslacht.clear()
        self.beschikkingsbevoegdheid.clear()
        self.aanduiding_naam.clear()
        self.land.clear()
        self.adressen.clear()
        self.rechtsvorm.clear()

    def process(self):
        subjects = uva2.process_csv(self.path, 'BRK_kadastraal_Subject', self.process_subject)

        models.Adres.objects.bulk_create(self.adressen.values(), batch_size=database.BATCH_SIZE)
        models.KadastraalSubject.objects.bulk_create(subjects, batch_size=database.BATCH_SIZE)

    def process_subject(self, row):
        subject_type = row['SJT_TYPE']

        woonadres_id = self.get_adres(row['SWS_OPENBARERUIMTENAAM'],
                                      row['SWS_HUISNUMMER'], row['SWS_HUISLETTER'], row['SWS_HUISNUMMERTOEVOEGING'],
                                      row['SWS_POSTCODE'], row['SWS_WOONPLAATSNAAM'],
                                      None, None, None,
                                      row['SWS_BUITENLAND_ADRES'], row['SWS_BUITENLAND_WOONPLAATS'],
                                      row['SWS_BUITENLAND_REGIO'], row['SWS_BUITENLAND_NAAM'],
                                      row['SWS_BUITENLAND_CODE'], row['SWS_BUITENLAND_OMS'])

        postadres_id = self.get_adres(row['SPS_OPENBARERUIMTENAAM'],
                                      row['SPS_HUISNUMMER'], row['SPS_HUISLETTER'], row['SPS_HUISNUMMERTOEVOEGING'],
                                      row['SPS_POSTCODE'], row['SPS_WOONPLAATSNAAM'],
                                      row['SPS_POSTBUSNUMMER'], row['SPS_POSTBUS_POSTCODE'],
                                      row['SPS_POSTBUS_WOONPLAATSNAAM'],
                                      row['SPS_BUITENLAND_ADRES'], row['SPS_BUITENLAND_WOONPLAATS'],
                                      row['SPS_BUITENLAND_REGIO'], row['SPS_BUITENLAND_NAAM'],
                                      row['SPS_BUITENLAND_CODE'], row['SPS_BUITENLAND_OMS'])

        if subject_type == "NATUURLIJK PERSOON":
            return self.process_natuurlijk(row, woonadres_id, postadres_id)
        else:
            return self.process_niet_natuurlijk(row, woonadres_id, postadres_id)

    def process_natuurlijk(self, row, woonadres_id, postadres_id):
        bron = models.KadastraalSubject.BRON_REGISTRATIE if row['SJT_NAAM'] else models.KadastraalSubject.BRON_KADASTER

        return models.KadastraalSubject(
                pk=row['BRK_SJT_ID'],
                type=models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK,
                beschikkingsbevoegdheid=self.get_beschikkingsbevoegdheid(row['SJT_BESCHIKKINGSBEVOEGDH_CODE'],
                                                                         row['SJT_BESCHIKKINGSBEVOEGDH_OMS']),
                voornamen=row['SJT_NP_VOORNAMEN'] or row['SJT_KAD_VOORNAMEN'],
                voorvoegsels=row['SJT_NP_VOORVOEGSELSGESLSNAAM'] or row['SJT_KAD_VOORVOEGSELSGESLSNAAM'],
                naam=row['SJT_NAAM'] or row['SJT_KAD_GESLACHTSNAAM'],
                geslacht=self.get_geslacht(row['SJT_NP_GESLACHTSCODE'] or row['SJT_KAD_GESLACHTSCODE'],
                                           row['SJT_NP_GESLACHTSCODE_OMS'] or row['SJT_KAD_GESLACHTSCODE_OMS']),
                aanduiding_naam=self.get_aanduiding_naam(row['SJT_NP_AANDUIDINGNAAMGEBR_CODE'],
                                                         row['SJT_NP_AANDUIDINGNAAMGEBR_OMS']),
                geboortedatum=row['SJT_NP_GEBOORTEDATUM'] or row['SJT_KAD_GEBOORTEDATUM'],
                geboorteplaats=row['SJT_NP_GEBOORTEPLAATS'] or row['SJT_KAD_GEBOORTEPLAATS'],
                geboorteland=self.get_land(row['SJT_NP_GEBOORTELAND_CODE'] or row['SJT_KAD_GEBOORTELAND_CODE'],
                                           row['SJT_NP_GEBOORTELAND_OMS'] or row['SJT_KAD_GEBOORTELAND_OMS']),
                overlijdensdatum=row['SJT_NP_DATUMOVERLIJDEN'] or row['SJT_KAD_DATUMOVERLIJDEN'],

                partner_voornamen=row['SJT_NP_VOORNAMEN_PARTNER'],
                partner_voorvoegsels=row['SJT_NP_VOORVOEGSEL_PARTNER'],
                partner_naam=row['SJT_NP_GESLACHTSNAAM_PARTNER'],

                land_waarnaar_vertrokken=self.get_land(row['SJT_NP_LANDWAARNAARVERTR_CODE'],
                                                       row['SJT_NP_LANDWAARNAARVERTR_OMS']),

                woonadres_id=woonadres_id,
                postadres_id=postadres_id,

                bron=bron,
        )

    def process_niet_natuurlijk(self, row, woonadres_id, postadres_id):
        bron = (models.KadastraalSubject.BRON_REGISTRATIE if row['SJT_NNP_STATUTAIRE_NAAM']
                else models.KadastraalSubject.BRON_KADASTER)

        return models.KadastraalSubject(
                pk=row['BRK_SJT_ID'],
                type=models.KadastraalSubject.SUBJECT_TYPE_NIET_NATUURLIJK,

                beschikkingsbevoegdheid=self.get_beschikkingsbevoegdheid(row['SJT_BESCHIKKINGSBEVOEGDH_CODE'],
                                                                         row['SJT_BESCHIKKINGSBEVOEGDH_OMS']),
                rsin=row['SJT_NNP_RSIN'],
                kvknummer=row['SJT_NNP_KVKNUMMER'],
                rechtsvorm=self.get_rechtsvorm(row['SJT_NNP_RECHTSVORM_CODE'] or row['SJT_KAD_RECHTSVORM_CODE'],
                                               row['SJT_NNP_RECHTSVORM_OMS'] or row['SJT_KAD_RECHTSVORM_OMS']),
                statutaire_naam=row['SJT_NNP_STATUTAIRE_NAAM'] or row['SJT_KAD_STATUTAIRE_NAAM'],
                statutaire_zetel=row['SJT_NNP_STATUTAIRE_ZETEL'] or row['SJT_KAD_STATUTAIRE_ZETEL'],

                woonadres_id=woonadres_id,
                postadres_id=postadres_id,

                bron=bron,
        )

    def get_geslacht(self, code, omschrijving):
        return _get_related(code, omschrijving, self.geslacht, models.Geslacht)

    def get_beschikkingsbevoegdheid(self, code, omschrijving):
        return _get_related(code, omschrijving, self.beschikkingsbevoegdheid, models.Beschikkingsbevoegdheid)

    def get_aanduiding_naam(self, code, omschrijving):
        return _get_related(code, omschrijving, self.aanduiding_naam, models.AanduidingNaam)

    def get_land(self, code, omschrijving):
        return _get_related(code, omschrijving, self.land, models.Land)

    def get_rechtsvorm(self, code, omschrijving):
        return _get_related(code, omschrijving, self.rechtsvorm, models.Rechtsvorm)

    def get_adres(self, openbareruimte_naam, huisnummer, huisletter, toevoeging, postcode, woonplaats, postbus_nummer,
                  postbus_postcode, postbus_woonplaats, buitenland_adres, buitenland_woonplaats, buitenland_regio,
                  buitenland_naam, buitenland_code, buitenland_omschrijving):

        values = [openbareruimte_naam, huisnummer, huisletter, toevoeging, postcode, woonplaats, postbus_nummer,
                  postbus_postcode, postbus_woonplaats, buitenland_adres, buitenland_woonplaats, buitenland_regio,
                  buitenland_naam, buitenland_code, buitenland_omschrijving]

        if not any(values):
            return None

        m = hashlib.md5()
        for v in values:
            m.update(str(v).encode('utf-8'))
        adres_id = m.hexdigest()

        try:
            huisnummer_int = int(huisnummer) if huisnummer else None
        except ValueError:
            huisnummer_int = None

        self.adressen.setdefault(adres_id, models.Adres(
                id=adres_id,

                openbareruimte_naam=openbareruimte_naam,
                huisnummer=huisnummer_int,
                huisletter=huisletter,
                toevoeging=toevoeging,
                postcode=postcode,
                woonplaats=woonplaats,
                postbus_nummer=int(postbus_nummer) if postbus_nummer else None,
                postbus_postcode=postbus_postcode,
                postbus_woonplaats=postbus_woonplaats,
                buitenland_adres=buitenland_adres,
                buitenland_woonplaats=buitenland_woonplaats,
                buitenland_regio=buitenland_regio,
                buitenland_naam=buitenland_naam,
                buitenland_land=self.get_land(buitenland_code, buitenland_omschrijving),
        ))
        return adres_id


class ImportKadastraalObjectTask(batch.BasicTask):
    name = "Import Kadastraal Object"

    def __init__(self, path):
        self.path = path
        self.secties = dict()
        self.soort_grootte = dict()
        self.cultuur_code_onbebouwd = dict()
        self.cultuur_code_bebouwd = dict()
        self.subjects = set()
        self.object_ids = set()

    def before(self):
        database.clear_models(
                models.APerceelGPerceelRelatie,
                models.KadastraalObject,
                models.SoortGrootte,
                models.CultuurCodeOnbebouwd,
                models.CultuurCodeBebouwd,
        )

        secties = models.KadastraleSectie.objects.select_related('kadastrale_gemeente').all()
        for s in secties:
            self.secties[(s.kadastrale_gemeente_id, s.sectie)] = s.pk

        self.subjects = set(models.KadastraalSubject.objects.values_list("id", flat=True))

    def after(self):
        self.secties.clear()
        self.soort_grootte.clear()
        self.cultuur_code_onbebouwd.clear()
        self.cultuur_code_bebouwd.clear()
        self.subjects.clear()
        self.object_ids.clear()

    def process(self):
        objects = dict(uva2.process_csv(self.path, 'BRK_kadastraal_object', self.process_object))
        models.KadastraalObject.objects.bulk_create(objects.values(), batch_size=database.BATCH_SIZE)

        self.object_ids = set(objects.keys())

        relaties = uva2.process_csv(self.path, 'BRK_kadastraal_object', self.process_relatie)
        models.APerceelGPerceelRelatie.objects.bulk_create(relaties, batch_size=database.BATCH_SIZE)

    def process_relatie(self, row):
        kot_id = row['BRK_KOT_ID']
        g_perceel_id = row['KOT_RELATIE_G_PERCEEL'] or None

        if not g_perceel_id:
            return

        if g_perceel_id not in self.object_ids:
            log.warn("Kadastraal Object {} references non-existing G-Perceel {}; skipping".format(kot_id, g_perceel_id))
            return

        return models.APerceelGPerceelRelatie(
            a_perceel_id=kot_id,
            g_perceel_id=g_perceel_id,
        )


    def process_object(self, row):
        kot_id = row['BRK_KOT_ID']

        kg_id = row['KOT_KADASTRALEGEMEENTE_CODE']
        sectie = row['KOT_SECTIE']
        if (kg_id, sectie) not in self.secties:
            log.warn("Kadastraal Object {} references non-existing Kadastrale Gemeente {}, Sectie {}; skipping".format(
                    kot_id, kg_id, sectie))
            return

        s_id = self.secties[(kg_id, sectie)]

        perceelnummer = row['KOT_PERCEELNUMMER']
        index_letter = row['KOT_INDEX_LETTER']
        index_nummer = row['KOT_INDEX_NUMMER']
        aanduiding = kadaster.get_aanduiding(kg_id, sectie, perceelnummer, index_letter, index_nummer)

        grootte = row['KOT_KADGROOTTE']
        koopsom = row['KOT_KOOPSOM']

        toestands_datum_str = row['KOT_TOESTANDSDATUM']
        toestands_datum = None
        try:
            toestands_datum = datetime.datetime.strptime(toestands_datum_str, "%Y%m%d%H%M%S").date()
        except ValueError:
            log.warn("Could not parse toestandsdatum {} for Kadastraal Object {}; ignoring".format(toestands_datum_str,
                                                                                                   kot_id))
            pass

        subject_id = row['BRK_SJT_ID'] or None
        if subject_id and subject_id not in self.subjects:
            log.warn("Kadastraal Object {} references non-existing Subject {}; ignoring".format(kot_id, subject_id))
            subject_id = None

        return kot_id, models.KadastraalObject(
                id=kot_id,
                kadastrale_gemeente_id=kg_id,
                aanduiding=aanduiding,
                sectie_id=s_id,
                perceelnummer=perceelnummer,
                index_letter=index_letter,
                index_nummer=index_nummer,
                soort_grootte=self.get_soort_grootte(row['KOT_SOORTGROOTTE_CODE'], row['KOT_SOORTGROOTTE_OMS']),
                grootte=int(grootte) if grootte else None,
                # TODO: Aanzetten wanneer levering correct ID bevat
                # g_perceel_id=row['KOT_RELATIE_G_PERCEEL'] or None,
                koopsom=int(koopsom) if koopsom else None,
                koopsom_valuta_code=row['KOT_KOOPSOM_VALUTA'],
                koopjaar=row['KOT_KOOPJAAR'],
                meer_objecten=row['KOT_INDICATIE_MEER_OBJECTEN'].lower() == 'j',
                cultuurcode_onbebouwd=self.get_cultuur_code_onbebouwd(row['KOT_CULTUURCODEONBEBOUWD_CODE'],
                                                                      row['KOT_CULTUURCODEONBEBOUWD_OMS']),
                cultuurcode_bebouwd=self.get_cultuur_code_bebouwd(row['KOT_CULTUURCODEBEBOUWD_CODE'],
                                                                  row['KOT_CULTUURCODEBEBOUWD_OMS']),

                register9_tekst=row['KOT_AKRREGISTER9TEKST'],
                status_code=row['KOT_STATUS_CODE'],
                toestandsdatum=toestands_datum,
                voorlopige_kadastrale_grens=row['KOT_IND_VOORLOPIGE_KADGRENS'].lower() != 'definitieve grens',
                in_onderzoek=row['KOT_INONDERZOEK'],

                geometrie=geo.get_multipoly(row['GEOMETRIE']),
                voornaamste_gerechtigde_id=subject_id,
        )

    def get_soort_grootte(self, code, omschrijving):
        return _get_related(code, omschrijving, self.soort_grootte, models.SoortGrootte)

    def get_cultuur_code_onbebouwd(self, code, omschrijving):
        return _get_related(code, omschrijving, self.cultuur_code_onbebouwd, models.CultuurCodeOnbebouwd)

    def get_cultuur_code_bebouwd(self, code, omschrijving):
        return _get_related(code, omschrijving, self.cultuur_code_bebouwd, models.CultuurCodeBebouwd)


class ImportZakelijkRechtTask(batch.BasicTask):
    name = "Import Zakelijk Recht"

    def __init__(self, path):
        self.path = path
        self.aard_zakelijk_recht = dict()
        self.splits_type = dict()
        self.kst = set()
        self.kot = set()

    def before(self):
        database.clear_models(
                models.ZakelijkRecht,
                models.AardZakelijkRecht,
                models.AppartementsrechtsSplitsType,
        )
        self.kst = set(models.KadastraalSubject.objects.values_list("id", flat=True))
        self.kot = set(models.KadastraalObject.objects.values_list("id", flat=True))

    def after(self):
        self.aard_zakelijk_recht.clear()
        self.kst.clear()
        self.kot.clear()
        self.splits_type.clear()

    def process(self):
        zrts = dict(uva2.process_csv(self.path, 'BRK_zakelijk_recht', self.process_subject))
        models.ZakelijkRecht.objects.bulk_create(zrts.values(), batch_size=database.BATCH_SIZE)

    def process_subject(self, row):
        zrt_id = row['BRK_ZRT_ID']
        tng_id = row['BRK_TNG_ID']

        if not tng_id:
            log.warn("Zakelijk recht {} has no TNG_ID; skipping".format(zrt_id))
            return

        kot_id = row['BRK_KOT_ID']
        if kot_id and kot_id not in self.kot:
            log.warn("Zakelijk recht {} references non-existing object {}; skipping".format(tng_id, kot_id))
            return

        kst_id = row['BRK_SJT_ID']
        if kst_id and kst_id not in self.kst:
            log.warn("Zakelijk recht {} references non-existing subject {}; skipping".format(tng_id, kst_id))
            return

        teller = row['TNG_AANDEEL_TELLER']
        noemer = row['TNG_AANDEEL_NOEMER']
        return tng_id, models.ZakelijkRecht(
                pk=tng_id,
                zrt_id=zrt_id,
                aard_zakelijk_recht=self.get_aardzakelijk_recht(row['ZRT_AARDZAKELIJKRECHT_CODE'],
                                                                row['ZRT_AARDZAKELIJKRECHT_OMS']),
                aard_zakelijk_recht_akr=row['ZRT_AARDZAKELIJKRECHT_AKR_CODE'],
                teller=int(teller) if teller else None,
                noemer=int(noemer) if noemer else None,
                ontstaan_uit_id=row['ZRT_ONTSTAAN_UIT'] or None,
                betrokken_bij_id=row['ZRT_BETROKKEN_BIJ'] or None,
                kadastraal_object_id=kot_id,
                kadastraal_subject_id=kst_id,
                kadastraal_object_status=row['KOT_STATUS_CODE'] or None,
                app_rechtsplitstype=self.get_appartementsrechts_splits_type(row['ASG_APP_RECHTSPLITSTYPE_CODE'],
                                                                            row['ASG_APP_RECHTSPLITSTYPE_OMS']),
        )

    def get_aardzakelijk_recht(self, code, omschrijving):
        return _get_related(code, omschrijving, self.aard_zakelijk_recht, models.AardZakelijkRecht)

    def get_appartementsrechts_splits_type(self, code, omschrijving):
        return _get_related(code, omschrijving, self.splits_type, models.AppartementsrechtsSplitsType)


class ImportAantekeningTask(batch.BasicTask):
    name = "Import Aantekeningen"

    def __init__(self, path):
        self.path = path
        self.aard_aantekening = dict()
        self.kst = set()
        self.kot = set()

    def before(self):
        database.clear_models(
                models.Aantekening,
                models.AardAantekening,
        )
        self.kst = set(models.KadastraalSubject.objects.values_list("id", flat=True))
        self.kot = set(models.KadastraalObject.objects.values_list("id", flat=True))

    def after(self):
        self.aard_aantekening.clear()
        self.kst.clear()
        self.kot.clear()

    def process(self):
        atks = dict(uva2.process_csv(self.path, 'BRK_aantekening', self.process_row))
        models.Aantekening.objects.bulk_create(atks.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, row):
        atk_id = row['BRK_ATG_ID']

        atk_type = row['ATG_TYPE']
        if atk_type == "Aantekening Zakelijk Recht (R)":
            return

        if atk_type != "Aantekening Kadastraal object (O)":
            log.warn("Aantekening {} has unknown type {}; skipping".format(atk_id, atk_type))
            return

        kot_id = row['BRK_KOT_ID'] or None
        if kot_id and kot_id not in self.kot:
            log.warn("Aantekening {} references non-existing object {}; skipping".format(atk_id, kot_id))
            return

        kst_id = row['BRK_SJT_ID'] or None
        if kst_id and kst_id not in self.kst:
            log.warn("Aantekening {} references non-existing subject {}; skipping".format(atk_id, kst_id))
            return

        return atk_id, models.Aantekening(
                pk=atk_id,
                aard_aantekening=self.get_aard_aantekening(row['ATG_AARDAANTEKENING_CODE'],
                                                           row['ATG_AARDAANTEKENING_OMS']),
                omschrijving=row['ATG_OMSCHRIJVING'],
                kadastraal_object_id=kot_id,
                opgelegd_door_id=kst_id,
        )

    def get_aard_aantekening(self, code, omschrijving):
        return _get_related(code, omschrijving, self.aard_aantekening, models.AardAantekening)


class ImportKadastraalObjectVerblijfsobjectTask(batch.BasicTask):
    name = "Import Kadaster - KOT-VBO"

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.kot = set()
        self.vbo = set()

    def before(self):
        database.clear_models(
                models.KadastraalObjectVerblijfsobjectRelatie,
        )
        self.kot = set(models.KadastraalObject.objects.values_list("id", flat=True))
        self.vbo = set(bag.Verblijfsobject.objects.values_list("id", flat=True))

    def after(self):
        self.kot.clear()
        self.vbo.clear()

    def process(self):
        rels = uva2.process_csv(self.path, "BRK_brk-bag", self.process_row)
        models.KadastraalObjectVerblijfsobjectRelatie.objects.bulk_create(rels, batch_size=database.BATCH_SIZE)

    def process_row(self, row):
        kot_id = row['BRK_KOT_ID']
        vbo_id = '0' + row['DIVA_VOT_ID']

        if not kot_id or kot_id not in self.kot:
            log.warn("BRK_BAG references non-existing kadastraal object {}; skipping".format(kot_id))
            return

        if not vbo_id or vbo_id not in self.vbo:
            log.warn("BRK_BAG references non-existing verblijfsobject {}; skipping".format(vbo_id))
            return

        return models.KadastraalObjectVerblijfsobjectRelatie(
                verblijfsobject_id=vbo_id,
                kadastraal_object_id=kot_id,
        )


class ImportKadasterJob(object):
    name = "Import Kadaster - BRK"

    def __init__(self):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))

        self.brk = os.path.join(diva, 'brk')
        self.brk_shp = os.path.join(diva, 'brk_shp')

    def tasks(self):
        return [
            ImportGemeenteTask(self.brk_shp),
            ImportKadastraleGemeenteTask(self.brk_shp),
            ImportKadastraleSectieTask(self.brk_shp),
            ImportKadastraalSubjectTask(self.brk),
            ImportKadastraalObjectTask(self.brk),
            ImportZakelijkRechtTask(self.brk),
            ImportAantekeningTask(self.brk),
            ImportKadastraalObjectVerblijfsobjectTask(self.brk),
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
