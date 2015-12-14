import datetime
import hashlib
import logging

from batch import batch
from datasets.brk import models
from datasets.generic import geo, database, uva2, kadaster

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
            log.warn(
                "Kadastrale sectie {} references non-existing Kadastrale Gemeente {}; skipping".format(pk, kad_gem_id))
            return

        return models.KadastraleSectie(
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
        subjects = uva2.process_csv(self.path, 'Kadastraal_Subject', self.process_subject)

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
            bsn=row['SJT_BSN'] or None,
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

        self.adressen.setdefault(adres_id, models.Adres(
            id=adres_id,

            openbareruimte_naam=openbareruimte_naam,
            huisnummer=int(huisnummer) if huisnummer else None,
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

    def before(self):
        database.clear_models(
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

    def process(self):
        objects = uva2.process_csv(self.path, 'Kadastraal_object', self.process_object)
        models.KadastraalObject.objects.bulk_create(objects, batch_size=database.BATCH_SIZE)

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

        return models.KadastraalObject(
            id=kot_id,
            kadastrale_gemeente_id=kg_id,
            aanduiding=aanduiding,
            sectie_id=s_id,
            perceelnummer=perceelnummer,
            index_letter=index_letter,
            index_nummer=index_nummer,
            soort_grootte=self.get_soort_grootte(row['KOT_SOORTGROOTTE_CODE'], row['KOT_SOORTGROOTTE_OMS']),
            grootte=int(grootte) if grootte else None,
            g_perceel_id=row['KOT_RELATIE_G_PERCEEL'] or None,
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
        zrts = uva2.process_csv(self.path, 'Zakelijk_Recht', self.process_subject)
        models.ZakelijkRecht.objects.bulk_create(zrts, batch_size=database.BATCH_SIZE)

    def process_subject(self, row):
        zrt_id = row['BRK_ZRT_ID']

        kot_id = row['BRK_KOT_ID']
        if kot_id and kot_id not in self.kot:
            log.warn("Zakelijk recht {} references non-existing object {}; skipping".format(zrt_id, kot_id))
            return

        kst_id = row['BRK_SJT_ID']
        if kst_id and kst_id not in self.kst:
            log.warn("Zakelijk recht {} references non-existing subject {}; skipping".format(zrt_id, kst_id))
            return

        return models.ZakelijkRecht(
            pk=zrt_id,
            aard_zakelijk_recht=self.get_aardzakelijk_recht(row['ZRT_AARDZAKELIJKRECHT_CODE'],
                                                            row['ZRT_AARDZAKELIJKRECHT_OMS']),
            aard_zakelijk_recht_akr=row['ZRT_AARDZAKELIJKRECHT_AKR_CODE'],
            # belast_azt=None,  # models.CharField(max_length=15)
            # belast_met_azt=None,  # models.CharField(max_length=15)
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


"""
ZRT_BELAST_AZT
Dit zakelijk recht belast de volgende Aardzakelijkrechten
VARCHAR2(15)
ZRT_BELAST_MET_AZT
Dit zakelijk recht is belast met de volgende Aardzakelijkrechten
VARCHAR2(15)
"""
