# Python
import logging
import os
import time
# Packages
from collections import defaultdict

from django.conf import settings
from django.db import connection
from django.utils.text import slugify
# Project
from search import index
from batch import batch
from datasets.generic import uva2, database, geo, metadata
from . import models, documents

log = logging.getLogger(__name__)

GOB_CSV_ENCODING = 'utf-8-sig'


class ImportGemeenteTask(batch.BasicTask):
    """
    Gemeente is not delivered by GOB. So we hardcode gemeente Amsterdam data
    """
    name = "Import gemeente code / naam"
    data = [
        ('03630000000000','0363','Amsterdam','','J','','GVI','N','19000101','')
    ]

    def __init__(self, path):
        self.path = path

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        gemeentes = [
            models.Gemeente(
                pk=r[0],
                code=r[1],
                naam=r[2],
                verzorgingsgebied=uva2.uva_indicatie(
                    r[4]),
                vervallen=uva2.uva_indicatie(r[8]),
                begin_geldigheid=uva2.uva_datum(
                    r[8]),
                einde_geldigheid=uva2.uva_datum(
                    r[9]),
            ) for r in self.data]

        models.Gemeente.objects.bulk_create(
            gemeentes, batch_size=database.BATCH_SIZE)


class ImportStadsdeelTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import stadsdeel"
    dataset_id = 'gebieden-stadsdeel'

    def __init__(self, bag_path):
        self.bag_path = bag_path
        self.gemeentes = dict()
        self.stadsdelen = dict()
        self.source = os.path.join(self.bag_path, 'GBD_stadsdeel_Actueel.csv')

    def before(self):
        self.gemeentes = dict(models.Gemeente.objects.values_list("code", "pk"))
        assert self.gemeentes

    def after(self):
        self.gemeentes.clear()
        self.stadsdelen.clear()
        self.update_metadata_csv(self.source)

        validate_geometry(models.Stadsdeel)

    def process(self):
        self.stadsdelen = dict(
            uva2.process_csv(None, None, self.process_row, source=self.source, encoding=GOB_CSV_ENCODING))

        models.Stadsdeel.objects.bulk_create(
            self.stadsdelen.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pk = r['identificatie']
        code = r['code']
        gemeente_id = self.gemeentes.get(r['ligtIn:BRK.GME.identificatie'])
        naam = r['naam']
        brondocument_naam = r['documentnummer']
        brondocument_datum = uva2.iso_datum(r['documentdatum'])
        ingang_cyclus = uva2.iso_datum(r['beginGeldigheid'])
        begin_geldigheid = uva2.iso_datum(r['beginGeldigheid'])
        einde_geldigheid = uva2.iso_datum(r['eindGeldigheid'])
        vervallen = None

        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_multipoly(wkt_geometrie)
            if not geometrie:
                log.error(f"Stadsdeel {code} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Stadsdeel {code}, {naam} has no geometry")
            geometrie = None

        if not uva2.datum_geldig(begin_geldigheid, einde_geldigheid):
            return None
        return code, models.Stadsdeel(
            pk=pk,
            code=code,
            naam=naam,
            brondocument_naam=brondocument_naam,
            brondocument_datum=brondocument_datum,
            ingang_cyclus=ingang_cyclus,
            vervallen=vervallen,
            gemeente_id=gemeente_id,
            begin_geldigheid=begin_geldigheid,
            einde_geldigheid=einde_geldigheid,
            geometrie=geometrie
        )


class ImportBuurtTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import BRT - BUURT"
    dataset_id = 'gebieden-buurt'

    def __init__(self, uva_path):
        self.uva_path = uva_path
        self.stadsdelen = set()
        self.buurten = dict()
        self.buurtcombinaties = dict()
        self.source = os.path.join(self.uva_path, 'GBD_buurt_Actueel.csv')

    def before(self):
        # database.clear_models(models.Buurt)
        self.stadsdelen = set(
            models.Stadsdeel.objects.values_list("pk", flat=True))
        self.buurtcombinaties = dict(
            models.Buurtcombinatie.objects.values_list("code", "pk"))

    def after(self):
        self.stadsdelen.clear()
        self.buurten.clear()
        self.buurtcombinaties.clear()
        self.update_metadata_csv(self.source)
        validate_geometry(models.Buurt)

        log.info("%d Buurten imported", models.Buurt.objects.count())

    def process(self):
        self.buurten = dict(
            uva2.process_csv(None, None, self.process_row, source=self.source, encoding=GOB_CSV_ENCODING))

        models.Buurt.objects.bulk_create(
            self.buurten.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pk = r['identificatie']
        stadsdeel_id = r['ligtIn:GBD.SDL.identificatie']
        vollcode = r['code']
        code = vollcode[1:]
        naam = r['naam']
        brondocument_naam = r['documentnummer']
        brondocument_datum = uva2.iso_datum(r['documentdatum'])
        ingang_cyclus = uva2.iso_datum(r['beginGeldigheid'])
        begin_geldigheid = uva2.iso_datum(r['beginGeldigheid'])
        einde_geldigheid = uva2.iso_datum(r['eindGeldigheid'])
        bc_voll_code = r['ligtIn:GBD.WIJK.code']
        bc_code = bc_voll_code[1:]
        vervallen = None

        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_multipoly(wkt_geometrie)
            if not geometrie:
                log.error(f"Buurt {naam} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Buurt {naam} has no geometry")
            geometrie = None

        if not uva2.datum_geldig(begin_geldigheid, einde_geldigheid):
            return None
        if stadsdeel_id not in self.stadsdelen:
            log.warning("""
            Buurt {} references non-existing stadsdeel {}; skipping
            """.format(pk, stadsdeel_id))
            return None

        bc_id = self.buurtcombinaties.get(bc_code)

        if not bc_id:
            log.warning("""
            Buurt {} references non-existing buurtcombinatie {}; ignoring
            """.format(pk, bc_code))

        return code, models.Buurt(
            pk=pk,
            code=code,
            vollcode=vollcode,
            naam=naam,
            brondocument_naam=brondocument_naam,
            brondocument_datum=brondocument_datum,
            ingang_cyclus=ingang_cyclus,
            stadsdeel_id=stadsdeel_id,
            vervallen=vervallen,
            begin_geldigheid=begin_geldigheid,
            einde_geldigheid=einde_geldigheid,
            buurtcombinatie_id=bc_id,
            geometrie=geometrie,
        )


class ImportBouwblokTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import BBK  - Bouwblok"
    dataset_id = 'gebieden-bouwblok'

    def __init__(self, uva_path):
        self.uva_path = uva_path
        self.buurten = set()
        self.bouwblokken = dict()
        self.source = os.path.join(self.uva_path, 'GBD_bouwblok_Actueel.csv')

    def before(self):
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))
        assert self.buurten

    def after(self):
        self.buurten.clear()
        self.update_metadata_csv(self.source)
        validate_geometry(models.Bouwblok)
        log.info('%s Bouwblokken imported', models.Bouwblok.objects.count())

    def process(self):
        # loads the csv
        for bb in uva2.process_csv(None, None, self.process_row, source=self.source, encoding=GOB_CSV_ENCODING):
            bb.save()

    def process_row(self, r):
        pk = r['identificatie']
        code = r['code']
        buurt_id = r['ligtIn:GBD.BRT.identificatie']
        ingang_cyclus = uva2.iso_datum(r['beginGeldigheid'])
        begin_geldigheid = uva2.iso_datum(r['beginGeldigheid'])
        einde_geldigheid = uva2.iso_datum(r['eindGeldigheid'])

        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_multipoly(wkt_geometrie)
            if not geometrie:
                log.error(f"Bouwblok {code} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Bouwblok {code} has no geometry")
            geometrie = None

        if buurt_id not in self.buurten:
            log.warning("""
             Bouwblok {} references non-existing buurt {}; fixing later.
             """.format(pk, buurt_id))
            buurt_id = None
        if not uva2.datum_geldig(begin_geldigheid, einde_geldigheid):
            return None
        return models.Bouwblok(
            pk=pk,
            code=code,
            ingang_cyclus=ingang_cyclus,
            buurt_id=buurt_id,
            begin_geldigheid=begin_geldigheid,
            einde_geldigheid=einde_geldigheid,
            geometrie=geometrie,
        )

        # add buurt to bouwblok if missing.
        # now dependent  objects like panden have
        # 'gebiedsinformation'
        if bouwblok.buurt is None:

            buurt = models.Buurt.objects.filter(
                geometrie__dwithin=(bouwblok.geometrie, 0))

            if buurt.count():
                buurt = buurt.first()
                bouwblok.buurt = buurt
                log.warning(
                    "Bouwblok %s connected to buurt %s;.",
                    bouwblok.id, buurt.naam)

        bouwblok.save()


class ImportWoonplaatsTask(batch.BasicTask):
    name = "Import woonplaats"

    def __init__(self, path):
        self.path = path
        self.gemeentes = dict()

    def before(self):
        self.gemeentes = dict(models.Gemeente.objects.values_list("code", "pk"))

    def after(self):
        self.gemeentes.clear()

    def process(self):

        source = os.path.join(self.path, 'BAG_woonplaats_Actueel.csv')
        woonplaatsen = uva2.process_csv(None, None, self.process_row, source=source, encoding=GOB_CSV_ENCODING)

        models.Woonplaats.objects.bulk_create(
            woonplaatsen, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pk = r['identificatie']
        gemeente_id = self.gemeentes.get(r['ligtIn:BRK.GME.identificatie'])
        values = {
            'pk': pk,
            'landelijk_id': pk,
            'naam': r['naam'],
            'document_nummer': r['documentnummer'],
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'vervallen': None,
            'gemeente_id': gemeente_id,
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        if not gemeente_id:
            log.warning("""
             Woonplaats {} references non-existing gemeente {}; skipping
             """.format(pk, gemeente_id))
            return None

        return models.Woonplaats(**values)


class ImportOpenbareRuimteTask(batch.BasicTask):
    name = "Import openbare ruimtes"

    def __init__(self, path):
        self.path = path
        self.bronnen = set()
        self.woonplaatsen = set()
        self.openbare_ruimtes = dict()
        self.omschijvingen = set()

    def store_opr_omschrijving(self, row):
        return row['identificatie'], row['beschrijving']

    def before(self):
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        self.types = dict([(t[1], t[0]) for t in models.OpenbareRuimte.TYPE_CHOICES])
        self.woonplaatsen = set(
            models.Woonplaats.objects.values_list("pk", flat=True))

        source = os.path.join(self.path, 'BAG_openbare_ruimte_beschrijving_Actueel.csv')

        self.omschrijvingen = dict(
            uva2.process_csv(
                None,
                None,
                self.store_opr_omschrijving,
                quotechar='"', source=source, encoding=GOB_CSV_ENCODING)
        )

    def after(self):
        self.bronnen.clear()
        self.woonplaatsen.clear()
        self.openbare_ruimtes.clear()
        self.types.clear()

    def process(self):
        source = os.path.join(self.path, 'BAG_openbare_ruimte_Actueel.csv')
        self.openbare_ruimtes = dict(
            uva2.process_csv(None, None, self.process_row, source=source, encoding=GOB_CSV_ENCODING))

        models.OpenbareRuimte.objects.bulk_create(
            self.openbare_ruimtes.values(), batch_size=database.BATCH_SIZE)

        validate_geometry(models.OpenbareRuimte)

    def process_row(self, r):
        pk = landelijk_id = r['identificatie']
        type = self.types.get(r['type'])
        if type is None:
            log.error(f"OpenbareRuimte {pk} has invalid type {r['type']}; skipping")
            return None

        naam = r['naam']
        naam_nen = r['naamNEN']
        if len(naam_nen) > 24:
            log.warning(f"OpenbareRuimte {pk}  naamNEN {naam_nen} longer then 24 characters")
            naam_nen = naam_nen[:24]

        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_multipoly(wkt_geometrie)
            if not geometrie:
                log.error(f"OpenbareRuimte {landelijk_id} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"OpenbareRuimte {landelijk_id}, {naam} has no geometry")
            geometrie = None

        values = {
            'pk': landelijk_id,
            # 'bron_id': None,
            'woonplaats_id': r['ligtIn:BAG.WPS.identificatie'],
            'landelijk_id': landelijk_id,
            'type': type,
            'naam': naam,
            # 'code': None,
            'status': (r['status']),
            'document_nummer': r['documentnummer'],
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'naam_nen': naam_nen,
            # 'vervallen': None,  # TODO: ? Perhaps if daterange not geldig
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
            'geometrie': geometrie
        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        if values['woonplaats_id'] not in self.woonplaatsen:
            log.warning("""
            OpenbareRuimte {} references non-existing woonplaats {}; skipping
            """.format(pk, values['woonplaats_id']))
            return None

        if landelijk_id:
            omschrijving = self.omschrijvingen.get(landelijk_id, None)
            values['omschrijving'] = omschrijving

        return pk, models.OpenbareRuimte(**values)


class ImportNummeraanduidingTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import nummeraanduiding"
    dataset_id = 'BAG'

    def __init__(self, path):
        self.path = path
        self.openbare_ruimtes = set()
        self.ligplaatsen = set()
        self.standplaatsen = set()
        self.verblijfsobjecten = set()
        self.source = os.path.join(self.path, 'BAG_nummeraanduiding_Actueel.csv')
        self.type_lookup = { object_type[1]: object_type[0] for object_type in models.Nummeraanduiding.OBJECT_TYPE_CHOICES}
        self.count = 0
        self.prev_time = time.time()

    def before(self):
        log.debug('Starting import nummeraanduidingen: delete old data')
        models.Nummeraanduiding.objects.all().delete()
        self.openbare_ruimtes = set(
            models.OpenbareRuimte.objects.values_list("pk", flat=True))
        self.ligplaatsen = set(models.Ligplaats.objects.values_list("pk", flat=True))
        self.standplaatsen = set(models.Standplaats.objects.values_list("pk", flat=True))
        self.verblijfsobjecten = set(models.Verblijfsobject.objects.values_list("pk", flat=True))

    def after(self):
        self.verblijfsobjecten.clear()
        self.standplaatsen.clear()
        self.ligplaatsen.clear()
        self.openbare_ruimtes.clear()
        self.update_metadata_csv(self.source)
        self.type_lookup.clear()
        log.info('%d Nummeraanduiding Imported', models.Nummeraanduiding.objects.count())

    def process(self):
        nummeraanduidingen = uva2.process_csv(None, None, self.process_row, source=self.source, encoding=GOB_CSV_ENCODING, max_rows=None)
        models.Nummeraanduiding.objects.bulk_create(
            nummeraanduidingen, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pk = landelijk_id = r['identificatie']

        openbare_ruimte_id = r['ligtAan:BAG.ORE.identificatie'] or None

        if openbare_ruimte_id not in self.openbare_ruimtes:
            log.warning(f'Nummeraanduiding {pk} references non-existing openbare ruimte {openbare_ruimte_id}; skipping')
            return None

        ligplaats_id = r['adresseert:BAG.LPS.identificatie'] or None
        if ligplaats_id and ligplaats_id not in self.ligplaatsen:
            log.warning(f'Nummeraanduiding {pk} references non-existing ligplaats {ligplaats_id}; set to None')
            ligplaats_id = None
        standplaats_id  = r['adresseert:BAG.SPS.identificatie'] or None
        if standplaats_id and standplaats_id not in self.standplaatsen:
            log.warning(f'Nummeraanduiding {pk} references non-existing standplaats {standplaats_id}; set to None')
            standplaats_id = None
        verblijfsobject_id =  r['adresseert:BAG.VOT.identificatie'] or None
        if verblijfsobject_id and verblijfsobject_id not in self.verblijfsobjecten:
            log.warning(f'Nummeraanduiding {pk} references non-existing verblijfsobject {verblijfsobject_id}; set to None')
            verblijfsobject_id = None

        values = {
            'pk': pk,
            'landelijk_id': landelijk_id,
            'huisnummer': r['huisnummer'],
            'huisletter': r['huisletter'],
            'huisnummer_toevoeging': r['huisnummertoevoeging'],
            'postcode': r['postcode'],
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'document_nummer': r['documentnummer'],
            'type': self.type_lookup[r['typeAdresseerbaarObject']],
            'type_adres': r['typeAdres'] or None,
            'status': (r['status'] or None),
            'openbare_ruimte_id': openbare_ruimte_id,
            'ligplaats_id': ligplaats_id,
            'standplaats_id': standplaats_id,
            'verblijfsobject_id': verblijfsobject_id,
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        self.count += 1
        now_time = time.time()
        if now_time - self.prev_time > 10.0:  # Report every 10 seconds
            self.prev_time = now_time
            log.debug(f"Processed {self.count} nummeraanduidingen...")

        return models.Nummeraanduiding(**values)


class ImportLigplaatsTask(batch.BasicTask):
    name = "Import ligplaatsen"

    def __init__(self, bag_path):
        self.bag_path = bag_path
        self.bronnen = set()
        self.buurten = set()
        self.ligplaatsen = dict()

    def before(self):
        log.debug('Starting import ligplaats: delete old data')
        models.Ligplaats.objects.all().delete()
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))

    def after(self):
        self.bronnen.clear()
        self.buurten.clear()
        self.ligplaatsen.clear()

    def process(self):
        source = os.path.join(self.bag_path, 'BAG_ligplaats_Actueel.csv')
        self.ligplaatsen = dict(uva2.process_csv(None, None, self.process_row, source=source, encoding=GOB_CSV_ENCODING))

        models.Ligplaats.objects.bulk_create(self.ligplaatsen.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pk = landelijk_id = r['identificatie']
        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_poly(wkt_geometrie)
            if not geometrie:
                log.error(f"Ligplaats {landelijk_id} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Ligplaats {landelijk_id} has no geometry")
            geometrie = None

        values = {
            'pk': pk,
            'landelijk_id': landelijk_id,
            'vervallen': None,
            'document_nummer': r['documentnummer'],
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'bron_id': None,
            'status': (r['status']),
            'buurt_id': r['ligtIn:GBD.BRT.identificatie'] or None,
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
            'indicatie_in_onderzoek': uva2.get_janee_boolean(r['aanduidingInOnderzoek']),
            'indicatie_geconstateerd': uva2.get_janee_boolean(r['geconstateerd']),
            'geometrie': geometrie
        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        if values['buurt_id'] and values['buurt_id'] not in self.buurten:
            log.warning('Ligplaats {} references non-existing buurt {}; ignoring'.format(pk, values['buurt_id']))
            values['buurt_id'] = None

        return pk, models.Ligplaats(**values)

    def process_wkt_row(self, wkt_id, geometrie):
        key = '0' + wkt_id
        if key not in self.ligplaatsen:
            log.warning('Ligplaats/WKT {} references non-existing ligplaats {}; skipping'.format(wkt_id, key))
            return

        self.ligplaatsen[key].geometrie = geometrie


class ImportStandplaatsenTask(batch.BasicTask):
    name = "Import standplaatsen"

    def __init__(self, bag_path):
        self.bag_path = bag_path
        self.bronnen = set()
        self.buurten = set()

    def before(self):
        log.info('Starting import standplaatsen: delete old data')
        models.Standplaats.objects.all().delete()
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))

    def after(self):
        self.bronnen.clear()
        self.buurten.clear()

        validate_geometry(models.Standplaats)

        assert models.Standplaats.objects.filter(
            geometrie__isnull=True).count() == 0, "Standplaats zonder geometrie!"

        log.info('%s Standplaatsen', models.Standplaats.objects.count())

    def process(self):
        source = os.path.join(self.bag_path, 'BAG_standplaats_Actueel.csv')
        standplaatsen = uva2.process_csv(None, None, self.process_row, source=source, encoding=GOB_CSV_ENCODING)

        models.Standplaats.objects.bulk_create(standplaatsen, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        pk = landelijk_id = r['identificatie']
        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_poly(wkt_geometrie)
            if not geometrie:
                log.error(f"Standplaats {landelijk_id} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Standplaats {landelijk_id} has no geometry")
            geometrie = None

        values = {
            'pk': pk,
            'landelijk_id': landelijk_id,
            'vervallen': None,
            'document_nummer': r['documentnummer'],
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'bron_id': None,
            'status': (r['status']),
            'buurt_id': r['ligtIn:GBD.BRT.identificatie'] or None,
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
            'indicatie_in_onderzoek': uva2.get_janee_boolean(r['aanduidingInOnderzoek']),
            'indicatie_geconstateerd': uva2.get_janee_boolean(r['geconstateerd']),
            'geometrie': geometrie
        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        if values['buurt_id'] and values['buurt_id'] not in self.buurten:
            log.warning('Ligplaats {} references non-existing buurt {}; ignoring'.format(pk, values['buurt_id']))
            values['buurt_id'] = None

        return models.Standplaats(**values)


class ImportVerblijfsobjectTask(batch.BasicTask):
    name = "Import Verblijfsobjecten"

    def __init__(self, path):
        self.path = path
        self.bronnen = set()
        self.locaties_ingang = set()
        self.buurten = set()
        self.panden = set()
        self.pandrelatie = defaultdict(list)

        self.count = 0
        self.prev_time = time.time()

    def before(self):
        log.debug('Starting import verblijfsobject: delete old data')
        models.VerblijfsobjectPandRelatie.objects.all().delete()
        models.Verblijfsobject.objects.all().delete()
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))
        self.panden = set(models.Pand.objects.values_list("pk", flat=True))

    def after(self):
        self.bronnen.clear()
        self.locaties_ingang.clear()
        self.buurten.clear()
        self.panden.clear()

        def gen_pand_vbo_objects(dict1:dict):
            for pand_id, vbo_ids in dict1.items():
                for vbo_id in vbo_ids:
                    yield models.VerblijfsobjectPandRelatie(verblijfsobject_id=vbo_id, pand_id=pand_id)

        log.debug('Create pandrelaties...')
        pand_vbo_objects = gen_pand_vbo_objects(self.pandrelatie)
        models.VerblijfsobjectPandRelatie.objects.bulk_create(pand_vbo_objects, batch_size=database.BATCH_SIZE)
        self.pandrelatie.clear()

        log.info('%d Verblijfsobjecten Imported', models.Verblijfsobject.objects.count())

    def process(self):
        source = os.path.join(self.path, 'BAG_verblijfsobject_Actueel.csv')
        verblijfsobjecten = uva2.process_csv(None, None, self.process_row, source=source, encoding=GOB_CSV_ENCODING, max_rows=None)
        log.debug('Create verblijfsobjecten...')
        models.Verblijfsobject.objects.bulk_create(verblijfsobjecten, batch_size=database.BATCH_SIZE)
        validate_geometry(models.Verblijfsobject)

    def process_row(self, r):
        pk = landelijk_id = r['identificatie']
        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_point(wkt_geometrie)
            if not geometrie:
                log.error(f"Verblijfsobject {landelijk_id} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Verblijfsobject {landelijk_id} has no geometry")
            geometrie = None

        toegang = r['toegang'].split('|') if r['toegang'] else []
        gebruiksdoel = r['gebruiksdoel'].split('|')
        gebruiksdoel_woonfunctie = r['gebruiksdoelWoonfunctie'] or None
        gebruiksdoel_gezondheidszorgfunctie = r['gebruiksdoelGezondheidszorgfunctie'] or None

        values = {
            'pk': pk,
            'landelijk_id': landelijk_id,
            'geometrie': geometrie,
            'oppervlakte': uva2.uva_nummer(r['oppervlakte']),
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'document_nummer': r['documentnummer'],
            'verdieping_toegang': uva2.uva_nummer(r['verdiepingToegang']),
            'aantal_eenheden_complex': r['aantalEenhedenComplex'] or None,
            'bouwlagen': uva2.uva_nummer(r['aantalBouwlagen']),
            'hoogste_bouwlaag': uva2.uva_nummer(r['hoogsteBouwlaag']),
            'laagste_bouwlaag': uva2.uva_nummer(r['laagsteBouwlaag']),
            'aantal_kamers': uva2.uva_nummer(r['aantalKamers']),
            'reden_afvoer': r['redenafvoer'],
            'reden_opvoer': r['redenopvoer'],
            'eigendomsverhouding': r['eigendomsverhouding'],
            'gebruik': r['is:WOZ.WOB.soortObject'],
            'toegang': toegang,
            'gebruiksdoel': gebruiksdoel,
            'status': (r['status']),
            'buurt_id': r['ligtIn:GBD.BRT.identificatie'] or None,
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
            'indicatie_in_onderzoek': uva2.get_janee_boolean(r['aanduidingInOnderzoek']),
            'indicatie_geconstateerd': uva2.get_janee_boolean(r['geconstateerd']),
            'gebruiksdoel_woonfunctie': gebruiksdoel_woonfunctie,
            'gebruiksdoel_gezondheidszorgfunctie': gebruiksdoel_gezondheidszorgfunctie,

        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        pand_ids = r['ligtIn:BAG.PND.identificatie'] or None
        if pand_ids:
            pand_ids = pand_ids.split('|')
            for pand_id in pand_ids:
                if pand_id in self.panden:
                    self.pandrelatie[pand_id].append(pk)

        if values['buurt_id'] and values['buurt_id'] not in self.buurten:
            log.warning('Ligplaats {} references non-existing buurt {}; ignoring'.format(pk, values['buurt_id']))
            values['buurt_id'] = None
        self.count += 1
        now_time = time.time()
        if now_time - self.prev_time > 10.0:  # Report every 10 seconds
            self.prev_time = now_time
            log.debug(f"Processed {self.count} verblijfsobjecten...")

        return models.Verblijfsobject(**values)


class ImportPandTask(batch.BasicTask):
    name = "Import pand"

    def __init__(self, path):
        self.path = path
        self.bouwblokken = set()
        self.verblijfsobjecten = set()
        self.panden = dict()
        self.source = os.path.join(self.path, 'BAG_pand_Actueel.csv')
        self.count = 0
        self.prev_time = time.time()

    def before(self):
        log.debug('Starting import pand: delete old data')
        models.Pand.objects.all().delete()
        self.bouwblokken = set(models.Bouwblok.objects.values_list("pk", flat=True))
        self.verblijfsobjecten = set(models.Verblijfsobject.objects.values_list("pk", flat=True))

    def after(self):
        self.verblijfsobjecten.clear()
        self.panden.clear()
        self.bouwblokken.clear()

    def process(self):
        self.panden = dict(
            uva2.process_csv(None, None, self.process_row, source=self.source, encoding=GOB_CSV_ENCODING, max_rows=None))
        models.Pand.objects.bulk_create(self.panden.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):

        pk = landelijk_id = r['identificatie']
        wkt_geometrie = r['geometrie']
        if wkt_geometrie:
            geometrie = geo.get_poly(wkt_geometrie)
            if not geometrie:
                log.error(f"Pand {landelijk_id} has no valid geometry; skipping")
                return None
        else:
            log.warning(f"Pand {landelijk_id} has no geometry")
            geometrie = None

        bbk_id = r['ligtIn:GBD.BBK.identificatie'] or None

        if bbk_id and bbk_id not in self.bouwblokken:
            log.warning(f'Pand {pk} references non-existing bouwblok {bbk_id}; ignoring')
            bbk_id = None

        values = {
            'pk': pk,
            'landelijk_id': landelijk_id,
            'document_mutatie': uva2.iso_datum(r['documentdatum']),
            'document_nummer': r['documentnummer'],
            'pandnaam': r['naam'] or None,
            'ligging': r['ligging'] or None,
            'type_woonobject': r['typeWoonobject'] or None,
            'bouwjaar': uva2.uva_nummer(r['oorspronkelijkBouwjaar']),
            'bouwlagen': uva2.uva_nummer(r['aantalBouwlagen']),
            'laagste_bouwlaag': uva2.uva_nummer(r['laagsteBouwlaag']),
            'hoogste_bouwlaag': uva2.uva_nummer(r['hoogsteBouwlaag']),
            'status': (r['status'] or None),
            'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
            'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
            'bouwblok_id': bbk_id,
            'geometrie': geometrie
        }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        self.count += 1
        now_time = time.time()
        if now_time - self.prev_time > 10.0:  # Report every 10 seconds
            self.prev_time = now_time
            log.debug(f"Processed {self.count} panden...")

        return pk, models.Pand(**values)


BAG_DOC_TYPES = [
    documents.Bouwblok,
    documents.Gebied,
]


class DeleteGebiedIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['BAG_GEBIED']
    doc_types = [documents.Gebied]


class DeleteBouwblokIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['BAG_BOUWBLOK']
    doc_types = [documents.Bouwblok]


class DeleteNummerAanduidingIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['NUMMERAANDUIDING']
    doc_types = [documents.Nummeraanduiding]


class DeletePandTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['BAG_PAND']
    doc_types = [documents.Pand]


class IndexLigplaatsTask(index.ImportIndexTask):
    name = "index ligplaatsen"
    queryset = models.Ligplaats.objects.\
        prefetch_related('adressen').\
        prefetch_related('adressen__openbare_ruimte')

    def convert(self, obj):
        return documents.from_ligplaats(obj)


class IndexStandplaatsTask(index.ImportIndexTask):
    name = "index standplaatsen"
    queryset = models.Standplaats.objects.\
        prefetch_related('adressen').\
        prefetch_related('adressen__openbare_ruimte')

    def convert(self, obj):
        return documents.from_standplaats(obj)


class IndexVerblijfsobjectTask(index.ImportIndexTask):
    name = "index verblijfsobjecten"
    queryset = models.Verblijfsobject.objects.\
        prefetch_related('adressen').\
        prefetch_related('adressen__openbare_ruimte').\
        prefetch_related('gebruiksdoelen')

    def convert(self, obj):
        return documents.from_verblijfsobject(obj)


class IndexOpenbareRuimteTask(index.ImportIndexTask):
    name = "index openbare ruimtes"
    queryset = models.OpenbareRuimte.objects.prefetch_related('adressen')

    def convert(self, obj):
        return documents.from_openbare_ruimte(obj)


#########################################################
# gebieden tasks
#########################################################


class IndexUnescoTask(index.ImportIndexTask):
    name = "index unesco"
    queryset = models.Unesco.objects.all()

    def convert(self, obj):
        return documents.from_unesco(obj)


class IndexBuurtTask(index.ImportIndexTask):
    name = "index buurten"
    queryset = models.Buurt.objects.all()

    def convert(self, obj):
        return documents.from_buurt(obj)


class IndexBuurtcombinatieTask(index.ImportIndexTask):
    name = "index buurtcombinaties"
    queryset = models.Buurtcombinatie.objects.all()

    def convert(self, obj):
        return documents.from_buurtcombinatie(obj)


class IndexGebiedsgerichtWerkenTask(index.ImportIndexTask):
    name = "index gebiedsgerichtwerken"
    queryset = models.Gebiedsgerichtwerken.objects.all()

    def convert(self, obj):
        return documents.from_gebiedsgerichtwerken(obj)


class IndexStadsdeelTask(index.ImportIndexTask):
    name = "index stadsdeel"
    queryset = models.Stadsdeel.objects.all()

    def convert(self, obj):
        return documents.from_stadsdeel(obj)


class IndexGrootstedelijkgebiedTask(index.ImportIndexTask):
    name = "Index grootstedelijk"
    queryset = models.Grootstedelijkgebied.objects.all()

    def convert(self, obj):
        return documents.from_grootstedelijk(obj)


class IndexGemeenteTask(index.ImportIndexTask):
    name = "index gemeenten"
    queryset = models.Gemeente.objects.all()

    def convert(self, obj):
        return documents.from_gemeente(obj)


class IndexWoonplaatsTask(index.ImportIndexTask):
    name = "index woonplatsen"
    queryset = models.Woonplaats.objects.all()

    def convert(self, obj):
        return documents.from_woonplaats(obj)


##########################################################
##########################################################


class IndexNummerAanduidingTask(index.ImportIndexTask):
    name = "index nummer aanduidingen"
    queryset = models.Nummeraanduiding.objects.\
        prefetch_related('verblijfsobject').\
        prefetch_related('standplaats').\
        prefetch_related('ligplaats').\
        prefetch_related('openbare_ruimte')

    def convert(self, obj):
        return documents.from_nummeraanduiding_ruimte(obj)


class IndexPandTask(index.ImportIndexTask):
    name = "index pand"

    queryset = models.Pand.objects.only('landelijk_id', 'pandnaam')

    def convert(self, obj):
        return documents.from_pand(obj)


class IndexBouwblokTask(index.ImportIndexTask):
    name = "index bouwblokken"
    queryset = models.Bouwblok.objects.all()

    def convert(self, obj):
        return documents.from_bouwblok(obj)


# These files don't have a UVA file
class ImportWijkTask(batch.BasicTask):
    """
    layer.fields:

    ['ID', 'NAAM', 'CODE', 'VOLLCODE', 'DOCNR',
     'DOCDATUM', 'INGSDATUM', 'EINDDATUM']
    """

    name = "Import GBD Wijk"

    def __init__(self, shp_path):
        self.shp_path = shp_path
        self.stadsdelen = dict()

    def before(self):
        self.stadsdelen = dict(
            models.Stadsdeel.objects.values_list("code", "id"))

    def after(self):
        self.stadsdelen.clear()
        validate_geometry(models.Buurtcombinatie)

    def process(self):
        shp_file = "GBD_wijk.shp"
        geo.process_shp(
            self.shp_path, shp_file, self.process_feature)

    def process_feature(self, feat):

        vollcode = feat.get('code')
        code = vollcode[1:]
        stadsdeel_id = vollcode[:1]
        wijk = models.Buurtcombinatie(
            id=str(int(feat.get('id'))),
            naam=feat.get('naam'),
            code=code,
            vollcode=vollcode,
            brondocument_naam=feat.get('docnummer'),
            brondocument_datum=feat.get('docdatum') or None,
            ingang_cyclus=feat.get('begindatum') or None,
            geometrie=geo.get_multipoly(feat.geom.wkt),
            stadsdeel_id=self.stadsdelen.get(stadsdeel_id),
            begin_geldigheid=feat.get('begindatum') or None,
            einde_geldigheid=feat.get('einddatum') or None,
        )
        wijk.save()


def log_details_wrong_geometry(model):
    """
    log details of wrong geometry.
    postgres has function for that.
    easy debugging..
    """

    table = model._meta.db_table

    explain_error_sql = """
    SELECT id, reason(ST_IsValidDetail(geometrie)),
               ST_AsText(location(ST_IsValidDetail(geometrie))) as location
    FROM {}
    WHERE ST_IsValid(geometrie) = false;
    """.format(connection.ops.quote_name(table))

    with connection.cursor() as c:
        c.execute(explain_error_sql)

        row = c.fetchone()

        log.error(f'\n\n!!! WRONG GEOMETRY in {table} !!!\n\n')
        while row is not None:
            log.error(f'id: {row[0]} : {row[1]} : {row[2]}')
            row = c.fetchone()


def validate_geometry(model):
    """
    given model validdate geometry so we can properly log it.
    and crash.
    """
    invalid = model.objects.filter(
        geometrie__isvalid=False)

    count = invalid.count()

    if count:
        log.error(model)
        log.error([o.id for o in invalid])
        # print out details of wrong geometry. postgres has function for that.
        log_details_wrong_geometry(model)

    # crash if any errors.
    # TODO : enable when the following errors are resolved (BH 2019-0812)
    # 2019-08-08 09:50:58,008 - datasets.bag.batch_gob - ERROR - id: 0363300000002632 : Hole lies outside shell : POINT(114753.424 488283.005)
    # 2019-08-08 09:50:58,008 - datasets.bag.batch_gob - ERROR - id: 0363300000003244 : Hole lies outside shell : POINT(117741.112 486822.026)
    # 2019-08-08 09:50:58,009 - datasets.bag.batch_gob - ERROR - id: 0363300000006103 : Hole lies outside shell : POINT(126613.204 486912.153)
    # 2019-08-08 09:50:58,009 - datasets.bag.batch_gob - ERROR - id: 0363300011952026 : Hole lies outside shell : POINT(121743.574 492816.025)
    #    assert count == 0


def get_code_for_omschrijving(omschrijving, model, dictionary):
    if not omschrijving:
        return None
    code = dictionary.get(omschrijving)
    if not code:
        obj, created = model.get_or_create(omschrijving)
        code = obj.code
        dictionary[omschrijving] = code
        if created:
            log.info(f"Created new code {code} for {omschrijving} in {model.__name__}")
    return code


class ImportGebiedsgerichtwerkenTask(batch.BasicTask):
    """
    layer.fields:

    ['naam', 'code', 'sdl_code', ...]
    TODO : In GOB import the GBD_ggw_gebied has also a 14 digit ID . Do we need this ID in the current API ?
    """

    name = "Import GBD Gebiedsgerichtwerken"

    def __init__(self, shp_path):
        self.shp_path = shp_path
        self.stadsdelen = dict()

    def before(self):
        self.stadsdelen = dict(
            models.Stadsdeel.objects.values_list("code", "pk"))

        assert self.stadsdelen, "No stadsdelen found!"

    def after(self):
        """
        Validate geometry
        """
        self.stadsdelen.clear()
        validate_geometry(models.Gebiedsgerichtwerken)
        log.debug(
            '%d Gebiedsgerichtwerken gebieden', models.Gebiedsgerichtwerken.objects.count())

    def process(self):
        shp_file = "GBD_ggw_gebied.shp"
        geo.process_shp(
            self.shp_path, shp_file,
            self.process_feature)

    def process_feature(self, feat):
        sdl = feat.get('sdl_code')
        code = feat.get('code')
        naam = feat.get('naam')

        if sdl not in self.stadsdelen:
            log.warning(
                'Gebiedsgerichtwerken {} references non-existing stadsdeel {}; skipping'.format(sdl, sdl))
            return
        ggw = models.Gebiedsgerichtwerken(
            id=code,
            naam=naam,
            code=code,
            stadsdeel_id=self.stadsdelen[sdl],
            geometrie=geo.get_multipoly(feat.geom.wkt),
        )

        ggw.save()


class ImportGebiedsgerichtwerkenPraktijkgebiedenTask(batch.BasicTask):
    """
    layer.fields:

    ['naam', ...]
    TODO : In GOB import the GBD_ggw_praktijkgebied has also a 14 digit ID . Do we need this ID in the current API ?
    TODO : Currently no stadsdeel in GBD_ggw_praktijkgebied. It is in the GOB delivery. Do we need it ?
    """

    name = "Import GBD Gebiedsgerichtwerken praktijkgebieden"

    def __init__(self, shp_path):
        self.shp_path = shp_path

    def before(self):
        log.debug('Starting import ggw praktijkgebieden: %s', 'delete old data')
        models.GebiedsgerichtwerkenPraktijkgebieden.objects.all().delete()

    def after(self):
        """
        Validate geometry
        """
        validate_geometry(models.GebiedsgerichtwerkenPraktijkgebieden)
        log.debug(
            '%d Gebiedsgerichtwerken praktijkgebieden', models.GebiedsgerichtwerkenPraktijkgebieden.objects.count())

    def process(self):
        shp_file = "GBD_ggw_praktijkgebied.shp"
        geo.process_shp(
            self.shp_path, shp_file,
            self.process_feature)

    def process_feature(self, feat):
        naam = feat.get('naam')

        models.GebiedsgerichtwerkenPraktijkgebieden(
            naam=naam,
            geometrie=geo.get_multipoly(feat.geom.wkt),
        ).save()


class ImportGrootstedelijkgebiedTask(batch.BasicTask):
    """
    layer.fields:

    ['NAAM']
    ['TYPE']
    """

    name = "Import GBD Grootstedelijkgebied"

    def __init__(self, shp_path):
        self.shp_path = shp_path

    def before(self):
        pass

    def after(self):
        """
        Validate geometry
        """
        validate_geometry(models.Grootstedelijkgebied)

    def process(self):
        geo.process_shp(
            self.shp_path,
            "GBD_grootstedelijke_projecten.shp", self.process_feature)

    def process_feature(self, feat):
        naam = feat.get('NAAM')
        gsg_type = feat.get('TYPE')
        models.Grootstedelijkgebied(
            id=slugify(naam),
            naam=naam,
            gsg_type=gsg_type,
            geometrie=geo.get_multipoly(feat.geom.wkt),
        ).save()


class ImportUnescoTask(batch.BasicTask):
    """
    layer.fields:

    ['NAAM']
    """

    name = "Import GBD unesco"

    def __init__(self, shp_path):
        self.shp_path = shp_path

    def before(self):
        pass

    def after(self):
        """
        Validate geometry
        """
        validate_geometry(models.Unesco)

    def process(self):
        geo.process_shp(self.shp_path, "GBD_unesco.shp", self.process_feature)

    def process_feature(self, feat):
        naam = feat.get('NAAM')
        models.Unesco(
            id=slugify(naam),
            naam=naam,
            geometrie=geo.get_multipoly(feat.geom.wkt),
        ).save()


class DenormalizeDataTask(batch.BasicTask):
    name = "Denormalize BAG vbo / standplaats / ligplaats data"

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        update_vbo_sql = """
UPDATE bag_verblijfsobject vbo
SET _openbare_ruimte_naam = t.naam,
  _huisnummer             = t.huisnummer,
  _huisletter             = t.huisletter,
  _huisnummer_toevoeging  = t.huisnummer_toevoeging
FROM (
       SELECT
         num.verblijfsobject_id    AS vbo_id,
         opr.naam                  AS naam,
         num.huisnummer            AS huisnummer,
         num.huisletter            AS huisletter,
         num.huisnummer_toevoeging AS huisnummer_toevoeging
       FROM bag_nummeraanduiding num
         LEFT JOIN bag_openbareruimte opr ON num.openbare_ruimte_id = opr.id
       WHERE num.type_adres = 'Hoofdadres'
     ) t
WHERE vbo.id = t.vbo_id;
        """

        log.debug(update_vbo_sql)

        with connection.cursor() as c:
            c.execute(update_vbo_sql)

            update_ligplaats_sql = """
UPDATE bag_ligplaats lig
SET _openbare_ruimte_naam = t.naam,
  _huisnummer             = t.huisnummer,
  _huisletter             = t.huisletter,
  _huisnummer_toevoeging  = t.huisnummer_toevoeging
FROM (
       SELECT
         num.ligplaats_id          AS lig_id,
         opr.naam                  AS naam,
         num.huisnummer            AS huisnummer,
         num.huisletter            AS huisletter,
         num.huisnummer_toevoeging AS huisnummer_toevoeging
       FROM bag_nummeraanduiding num
         LEFT JOIN bag_openbareruimte opr ON num.openbare_ruimte_id = opr.id
       WHERE num.type_adres = 'Hoofdadres' AND num.ligplaats_id IS NOT NULL
     ) t
WHERE lig.id = t.lig_id;
            """
            log.debug(update_ligplaats_sql)

            c.execute(update_ligplaats_sql)

            update_standplaats_sql = """
UPDATE bag_standplaats sta
SET _openbare_ruimte_naam = t.naam,
  _huisnummer             = t.huisnummer,
  _huisletter             = t.huisletter,
  _huisnummer_toevoeging  = t.huisnummer_toevoeging
FROM (
       SELECT
         num.standplaats_id        AS sta_id,
         opr.naam                  AS naam,
         num.huisnummer            AS huisnummer,
         num.huisletter            AS huisletter,
         num.huisnummer_toevoeging AS huisnummer_toevoeging
       FROM bag_nummeraanduiding num
         LEFT JOIN bag_openbareruimte opr ON num.openbare_ruimte_id = opr.id
       WHERE num.type_adres = 'Hoofdadres' AND num.standplaats_id IS NOT NULL
     ) t
WHERE sta.id = t.sta_id;
            """

            log.debug(update_standplaats_sql)
            c.execute(update_standplaats_sql)

            update_nummeraanduiding_sql = """
UPDATE bag_nummeraanduiding num
SET _openbare_ruimte_naam = opr.naam
FROM bag_openbareruimte opr
WHERE opr.id = num.openbare_ruimte_id
            """

            log.debug(update_nummeraanduiding_sql)
            c.execute(update_nummeraanduiding_sql)

            update_geom_num_vbo_sql = """
UPDATE bag_nummeraanduiding num
SET _geom = vbo.geometrie
FROM bag_verblijfsobject vbo
WHERE num.verblijfsobject_id = vbo.id
            """

            log.debug(update_geom_num_vbo_sql)
            c.execute(update_geom_num_vbo_sql)

            update_geom_num_standplaats_sql = """
UPDATE bag_nummeraanduiding num
SET _geom = std.geometrie
FROM bag_standplaats std
WHERE num.standplaats_id = std.id
            """
            log.debug(update_geom_num_standplaats_sql)
            c.execute(update_geom_num_standplaats_sql)

            update_geom_num_ligplaats_sql = """
UPDATE bag_nummeraanduiding num
SET _geom = lig.geometrie
FROM bag_ligplaats lig
WHERE num.ligplaats_id = lig.id
        """
            log.debug(update_geom_num_ligplaats_sql)
            c.execute(update_geom_num_ligplaats_sql)


class UpdateGebiedenAttributenTask(batch.BasicTask):
    """
    Denormalize gebieden attributen op VBO / Nummeraanduidingen

    Add missing buurten aan bouwblokken.
    """

    name = "Denormalize gebiedsgericht werken data"

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        for ggw in models.Gebiedsgerichtwerken.objects.all():

            # add buurten to GGW
            buurten = models.Buurt.objects.filter(
                geometrie__within=ggw.geometrie)

            for b in buurten:
                ggw.buurten.add(b)

            vbos = models.Verblijfsobject.objects.filter(
                geometrie__within=ggw.geometrie)

            log.debug('Update Gebiedsgerichtwerken %s key %s VBO',
                      ggw.naam, vbos.count())

            vbos.update(_gebiedsgerichtwerken=ggw.id)

            standplaatsen = models.Standplaats.objects.filter(
                geometrie__within=ggw.geometrie)

            log.debug('Update Gebiedsgerichtwerken %s key %s Standplaats',
                      ggw.naam, standplaatsen.count())

            standplaatsen.update(_gebiedsgerichtwerken=ggw.id)

            ligplaatsen = models.Ligplaats.objects.filter(
                geometrie__within=ggw.geometrie)

            log.debug('Update Gebiedsgerichtwerken %s key %s Ligplaats',
                      ggw.naam, ligplaatsen.count())

            ligplaatsen.update(_gebiedsgerichtwerken=ggw.id)


class UpdateGrootstedelijkAttributenTask(batch.BasicTask):
    """
    Denormalize grootstedelijk gebieden attributen
    """

    name = "Denormalize grootstedelijke gebieden data"

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        for gsg in models.Grootstedelijkgebied.objects.all():
            vbos = models.Verblijfsobject.objects.filter(
                geometrie__within=gsg.geometrie)

            log.debug('Update Grootstedelijk %s key %s VBO',
                      gsg.naam, vbos.count())

            vbos.update(_grootstedelijkgebied=gsg.id)

            standplaatsen = models.Standplaats.objects.filter(
                geometrie__within=gsg.geometrie)

            log.debug('Update Grootstedelijk %s key %s Standplaats',
                      gsg.naam, standplaatsen.count())

            standplaatsen.update(_grootstedelijkgebied=gsg.id)

            ligplaatsen = models.Ligplaats.objects.filter(
                geometrie__within=gsg.geometrie)

            log.debug('Update Grootstedelijk %s key %s Ligplaats',
                      gsg.naam, ligplaatsen.count())

            ligplaatsen.update(_grootstedelijkgebied=gsg.id)


class ImportBagJob(object):
    name = "Import BAG"

    def __init__(self, **kwargs):
        diva = settings.DIVA_DIR
        if not os.path.exists(diva):
            raise ValueError("DIVA_DIR not found: {}".format(diva))
        self.bag_path = os.path.join(diva, 'bag')
        self.opr_beschrijving_path = os.path.join(diva, 'bag_openbareruimte_beschrijving')
        self.bag_wkt_path = os.path.join(diva, 'bag_wkt')
        self.gebieden_path = os.path.join(diva, 'gebieden')
        self.gebieden_shp_path = os.path.join(diva, 'gebieden_shp')
        gob_dir = settings.GOB_DIR
        if not os.path.exists(gob_dir):
            raise ValueError("GOB_DIR not found: {}".format(gob_dir))

        self.gob_gebieden_path = os.path.join(gob_dir, 'gebieden/CSV_Actueel')
        self.gob_gebieden_shp_path = os.path.join(gob_dir, 'gebieden/SHP')
        self.gob_bag_path = os.path.join(gob_dir, 'bag/CSV_Actueel')

    def tasks(self):

        return [
            # no-dependencies.
            ImportGemeenteTask(self.gebieden_path),
            ImportWoonplaatsTask(self.gob_bag_path),
            ImportStadsdeelTask(self.gob_gebieden_path),
            ImportWijkTask(self.gob_gebieden_shp_path),

            # stadsdelen.
            ImportGebiedsgerichtwerkenTask(self.gob_gebieden_shp_path),
            ImportGebiedsgerichtwerkenPraktijkgebiedenTask(self.gob_gebieden_shp_path),
            ImportGrootstedelijkgebiedTask(self.gebieden_shp_path),  # TODO : nog niet geleverd door GOB
            ImportUnescoTask(self.gebieden_shp_path),  # TODO : nog niet geleverd door GOB
            #
            ImportBuurtTask(self.gob_gebieden_path),
            ImportBouwblokTask(self.gob_gebieden_path),
            #
            ImportOpenbareRuimteTask(self.gob_bag_path),
            #
            ImportLigplaatsTask(self.gob_bag_path),
            ImportStandplaatsenTask(self.gob_bag_path),
            ImportPandTask(self.gob_bag_path),
            # large. 500.000
            ImportVerblijfsobjectTask(self.gob_bag_path),
            #
            # large. 500.000
            ImportNummeraanduidingTask(self.gob_bag_path),
            #
            # some sql copying fields
            DenormalizeDataTask(),
            #
            # more denormalizing sql
            UpdateGebiedenAttributenTask(),
            UpdateGrootstedelijkAttributenTask(),
        ]


class IndexBagJob(object):
    name = "Delete and Fill Nummeraanduiding search-index"

    def tasks(self):
        return [
            DeleteNummerAanduidingIndexTask(),
            IndexNummerAanduidingTask(),
        ]


class BuildIndexBagJob(object):
    name = "Fill Nummeraanduiding search-index"

    def tasks(self):
        return [
            IndexNummerAanduidingTask(),
        ]


class DeleteIndexBagJob(object):

    name = "Delete BAG related indexes"

    def tasks(self):
        return [
            DeleteNummerAanduidingIndexTask(),
        ]


class IndexPandJob(object):
    name = "Delete and Fill Pand search-index"

    def tasks(self):
        return [
            DeletePandTask(),
            IndexPandTask(),
        ]


class BuildIndexPandJob(object):
    name = "Fill Pand search-index"

    def tasks(self):
        return [
            IndexPandTask(),
        ]


class DeleteIndexPandJob(object):

    name = "Delete Pand related indexes"

    def tasks(self):
        return [
            DeletePandTask(),
        ]


class DeleteIndexGebiedJob(object):

    name = "Delete BAG_GEBIED index"

    def tasks(self):
        return [
            DeleteGebiedIndexTask(),
            DeleteBouwblokIndexTask(),
        ]


class IndexNummerAanduidingJob(object):
    name = "Create new search index for Nummeraanduiding"

    def tasks(self):
        return [
            DeleteNummerAanduidingIndexTask(),
            IndexNummerAanduidingTask()
        ]


class IndexGebiedenJob(object):
    """Important! This only adds to the bag index, but does not create it"""

    name = "Create add gebieden to BAG index"

    def tasks(self):
        return [
            IndexBouwblokTask(),
            IndexOpenbareRuimteTask(),
            IndexUnescoTask(),
            IndexBuurtTask(),
            IndexBuurtcombinatieTask(),
            IndexStadsdeelTask(),
            IndexGrootstedelijkgebiedTask(),
            IndexGebiedsgerichtWerkenTask(),
            IndexWoonplaatsTask(),
        ]
