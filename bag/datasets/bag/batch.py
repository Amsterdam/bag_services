# Python
import logging
import os
# Packages
from django.conf import settings
from django.contrib.gis.geos import Point, Polygon, MultiPolygon, GEOSGeometry
from django.db import connection
from django.utils.text import slugify
# Project
from search import index
from batch import batch
from datasets.generic import uva2, database, geo, metadata
from . import models, documents

log = logging.getLogger(__name__)


class CodeOmschrijvingUvaTask(batch.BasicTask):
    model = None
    code = None

    def __init__(self, path):
        self.path = path

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        avrs = uva2.process_uva2(self.path, self.code, self.process_row)
        self.model.objects.bulk_create(avrs, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        # noinspection PyCallingNonCallable
        return self.model(pk=r['Code'], omschrijving=r['Omschrijving'])


class ImportIndicatieAOTTask(batch.BasicTask):

    name = "import Indicatie Onderzoek Adresseerbaar Objecten AOT"

    def __init__(self, path, gob):
        self.gob = gob
        self.path = path

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        if self.gob:  # For GOB import not needed
            return
        try:
            self.indicaties = uva2.process_csv(
                self.path, 'AOT_geconstateerd-inonderzoek', self.process_row,
                with_header=False
            )
        except ValueError():
            # when delivery is all AOT below can be removed
            log.traceback('AOT missing trying old file')
            self.indicaties = uva2.process_csv(
                self.path, 'VBO_geconstateerd-inonderzoek', self.process_row,
                with_header=False
            )

        models.IndicatieAdresseerbaarObject.objects.bulk_create(
            self.indicaties, batch_size=database.BATCH_SIZE)

    def process_row(self, indicatie):

        landelijk_id = indicatie[0]

        indicatie_geconstateerd = False
        indicatie_in_onderzoek = False

        if indicatie[1] == 'J':
            indicatie_geconstateerd = True

        if indicatie[2] == 'J':
            indicatie_in_onderzoek = True

        return models.IndicatieAdresseerbaarObject(
            landelijk_id=landelijk_id,
            indicatie_geconstateerd=indicatie_geconstateerd,
            indicatie_in_onderzoek=indicatie_in_onderzoek
        )


class ImportPandNaamTask(batch.BasicTask):
    name = "Some Panden have nice names. Import those"

    def __init__(self, path):
        self.path = path

    def before(self):
        assert models.Pand.objects.count() > 0, "No panden present!"

    def after(self):
        pass

    def process(self):

        self.pandnamen = uva2.process_csv(
            self.path, 'PND_naam', self.process_row,
            with_header=False
        )

        for pandnaam in self.pandnamen:
            self.process_row(pandnaam)

    def process_row(self, pand_naam):
        p_id = pand_naam[0]
        naam = pand_naam[1]

        try:
            pand = models.Pand.objects.get(landelijk_id=p_id)
        except models.Pand.DoesNotExist:
            log.info(f'Pand id does not exist! skipping. {p_id}')
            return

        pand.pandnaam = naam
        pand.save()


class ImportAvrTask(CodeOmschrijvingUvaTask):
    name = "Import AVR"
    code = "AVR"
    model = models.RedenAfvoer


class ImportOvrTask(CodeOmschrijvingUvaTask):
    name = "Import OVR"
    code = "OVR"
    model = models.RedenOpvoer


class ImportBronTask(CodeOmschrijvingUvaTask):
    name = "Import BRN"
    code = "BRN"
    model = models.Bron


class ImportStatusTask(CodeOmschrijvingUvaTask):
    name = "Import STS - Status"
    code = "STS"
    model = models.Status


class ImportEgmTask(CodeOmschrijvingUvaTask):
    name = "Import EGM"
    code = "EGM"
    model = models.Eigendomsverhouding


class ImportFngTask(CodeOmschrijvingUvaTask):
    name = "Import FNG"
    code = "FNG"
    model = models.Financieringswijze


class ImportLggTask(CodeOmschrijvingUvaTask):
    name = "Import LGG"
    code = "LGG"
    model = models.Ligging


class ImportGbkTask(CodeOmschrijvingUvaTask):
    name = "Import GBK"
    code = "GBK"
    model = models.Gebruik


class ImportLocTask(CodeOmschrijvingUvaTask):
    name = "Import LOC"
    code = "LOC"
    model = models.LocatieIngang


class ImportTggTask(CodeOmschrijvingUvaTask):
    name = "Import TGG"
    code = "TGG"
    model = models.Toegang


class ImportGebruiksdoelenTask(batch.BasicTask):
    name = "Import Gebruiksdoel CSV"

    def __init__(self, path):
        self.path = path

    def before(self):
        self.pk_ids = models.Verblijfsobject.objects.values_list('pk', 'landelijk_id')
        self.vbo_bag_ids = {_id: pk for pk, _id in self.pk_ids}
        assert self.vbo_bag_ids

    def after(self):
        del self.pk_ids
        del self.vbo_bag_ids

    def process(self):
        self.gebruiksdoelen = uva2.process_csv(
            self.path, 'VBO_gebruiksdoelen', self.process_row,
            with_header=False
        )

        models.Gebruiksdoel.objects.bulk_create(
            self.gebruiksdoelen, batch_size=database.BATCH_SIZE)

    def process_row(self, doel):

        msg = 'Gebruiksdoel references non-existing landelijk BAG id: %s'

        landelijk_id = doel[0]

        if landelijk_id not in self.vbo_bag_ids:
            logging.warning(msg, landelijk_id)
            return None

        target_pk = self.vbo_bag_ids[landelijk_id]

        doel = doel + [''] * (5 - len(doel))
        # DP-5955 code_plus and omschrijving_plus is only valid for code 1000 or 1300
        if not (doel[1] == '1000' or doel[1] == '1300') and (doel[3] != '' or doel[4] != ''):
            doel[3] = doel[4] = ''

        return models.Gebruiksdoel(
            verblijfsobject_id=target_pk,
            code=doel[1],
            omschrijving=doel[2],
            code_plus=doel[3],
            omschrijving_plus=doel[4]
        )


class ImportGmeTask(batch.BasicTask):
    name = "Import GME Gemeente code / naam"

    def __init__(self, path):
        self.path = path

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        gemeentes = uva2.process_uva2(self.path, "GME", self.process_row)
        models.Gemeente.objects.bulk_create(
            gemeentes, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        return models.Gemeente(
            pk=r['sleutelVerzendend'],
            code=r['Gemeentecode'],
            naam=r['Gemeentenaam'],
            verzorgingsgebied=uva2.uva_indicatie(
                r['IndicatieVerzorgingsgebied']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            begin_geldigheid=uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
            einde_geldigheid=uva2.uva_datum(
                r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
        )


class ImportSdlTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import SDL"
    dataset_id = 'gebieden-stadsdeel'

    def __init__(self, bag_path, shp_path, gob):
        self.gob = gob
        self.shp_path = shp_path
        self.bag_path = bag_path
        self.gemeentes = set()
        self.stadsdelen = dict()
        if self.gob:
            self.source = os.path.join(self.bag_path, 'GBD_stadsdeel_Actueel.csv')

    def before(self):
        self.gemeentes = set(
            models.Gemeente.objects.values_list("pk", flat=True))

        assert self.gemeentes

    def after(self):
        self.gemeentes.clear()
        self.stadsdelen.clear()
        if self.gob:
            self.update_metadata_csv(self.source)
        else:
            self.update_metadata_uva2(self.bag_path, 'SDL')

        validate_geometry(models.Stadsdeel)

    def process(self):
        if self.gob:
            self.stadsdelen = dict(
                uva2.process_csv(None, None, self.process_row, source=self.source, encoding='utf-8'))
        else:
            self.stadsdelen = dict(
                uva2.process_uva2(self.bag_path, "SDL", self.process_row))

        geo.process_shp(
            self.shp_path, "GBD_stadsdeel.shp" if self.gob else "GBD_Stadsdeel.shp", self.process_feature)

        models.Stadsdeel.objects.bulk_create(
            self.stadsdelen.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if self.gob:
            pk = r['identificatie']
            code = r['code']
            gemeente_id = r['ligtIn:BRK.GME.identificatie']
            # The gemeente is in GOB in BRK and will be delivered much later.
            # For now we can use the one and only gemeente that is in the old import.
            if not gemeente_id:
                gemeente_id = next(iter(self.gemeentes))

            naam = r['naam']
            brondocument_naam = r['documentnummer']
            brondocument_datum = uva2.iso_datum(r['documentdatum'])
            ingang_cyclus = uva2.iso_datum(r['beginGeldigheid'])
            begin_geldigheid = uva2.iso_datum(r['beginGeldigheid'])
            einde_geldigheid = uva2.iso_datum(r['eindGeldigheid'])
            vervallen = None

        else:
            if not uva2.uva_geldig(r['SDLGME/TijdvakRelatie/begindatumRelatie'],
                                   r['SDLGME/TijdvakRelatie/einddatumRelatie']):
                return None

            pk = r['sleutelVerzendend']
            gemeente_id = r['SDLGME/GME/sleutelVerzendend'] or None

            if gemeente_id not in self.gemeentes:
                log.warning("""
                    Stadsdeel {} references non-existing gemeente {};
                    skipping""".format(
                    pk, gemeente_id))
                return None

            code = r['Stadsdeelcode']
            naam = r['Stadsdeelnaam']
            brondocument_naam = r['Brondocumentverwijzing']
            brondocument_datum = uva2.uva_datum(r['Brondocumentdatum'])
            ingang_cyclus = uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'])
            vervallen = uva2.uva_indicatie(r['Indicatie-vervallen'])
            begin_geldigheid = uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'])
            einde_geldigheid = uva2.uva_datum(
                r['TijdvakGeldigheid/einddatumTijdvakGeldigheid'])

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
        )

    def process_feature(self, feat):
        code = feat.get('code' if self.gob else 'CODE')
        if code not in self.stadsdelen:
            log.warning(
                """Stadsdeel/SHP {} references non-existing stadsdeel;
                skipping""".format(code))
            return

        self.stadsdelen[code].geometrie = geo.get_multipoly(feat.geom.wkt)


class ImportBuurtTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import BRT - BUURT"
    dataset_id = 'gebieden-buurt'

    def __init__(self, uva_path, shp_path, gob):
        self.gob = gob
        self.shp_path = shp_path
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
        if self.gob:
            self.update_metadata_csv(self.source)
        else:
            self.update_metadata_uva2(self.uva_path, 'BRT')
        validate_geometry(models.Buurt)

        log.info("%d Buurten imported", models.Buurt.objects.count())

    def process(self):
        if self.gob:
            self.buurten = dict(
                uva2.process_csv(None, None, self.process_row, source=self.source, encoding='utf-8'))
        else:
            self.buurten = dict(
                uva2.process_uva2(self.uva_path, "BRT", self.process_row))

        geo.process_shp(
            self.shp_path, "GBD_buurt.shp" if self.gob else "GBD_Buurt.shp", self.process_feature)

        models.Buurt.objects.bulk_create(
            self.buurten.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if self.gob:
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
        else:
            if not uva2.uva_geldig(r['BRTSDL/TijdvakRelatie/begindatumRelatie'],
                                   r['BRTSDL/TijdvakRelatie/einddatumRelatie']):
                return None

            pk = r['sleutelVerzendend']
            stadsdeel_id = r['BRTSDL/SDL/sleutelVerzendend'] or None

            code = r['Buurtcode']
            bc_code = code[:-1]

            naam = r['Buurtnaam']
            brondocument_naam = r['Brondocumentverwijzing']
            brondocument_datum = uva2.uva_datum(r['Brondocumentdatum'])
            ingang_cyclus = uva2.uva_datum(
                    r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'])
            vervallen = uva2.uva_indicatie(r['Indicatie-vervallen'])
            begin_geldigheid = uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'])
            einde_geldigheid = uva2.uva_datum(
                    r['TijdvakGeldigheid/einddatumTijdvakGeldigheid'])

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
            naam=naam,
            brondocument_naam=brondocument_naam,
            brondocument_datum=brondocument_datum,
            ingang_cyclus=ingang_cyclus,
            stadsdeel_id=stadsdeel_id,
            vervallen=vervallen,
            begin_geldigheid=begin_geldigheid,
            einde_geldigheid=einde_geldigheid,
            buurtcombinatie_id=bc_id,
        )

    def process_feature(self, feat):
        vollcode = feat.get('code' if self.gob else 'VOLLCODE')
        code = vollcode[1:]
        if code not in self.buurten:
            log.warning("""
            Buurt/SHP {} references non-existing buurt; skipping
            """.format(code))
            return

        self.buurten[code].geometrie = geo.get_multipoly(feat.geom.wkt)
        self.buurten[code].vollcode = vollcode


class ImportBouwblokTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import BBK  - Bouwblok"
    dataset_id = 'gebieden-bouwblok'

    def __init__(self, uva_path, shp_path, gob):
        self.gob = gob
        self.shp_path = shp_path
        self.uva_path = uva_path
        self.buurten = set()
        self.bouwblokken = dict()
        self.source = os.path.join(self.uva_path, 'GBD_bouwblok_Actueel.csv')

    def before(self):
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))
        assert self.buurten

    def after(self):
        self.buurten.clear()
        if self.gob:
            self.update_metadata_csv(self.source)
        else:
            self.update_metadata_uva2(self.uva_path, 'BBK')
        validate_geometry(models.Bouwblok)
        log.info('%s Bouwblokken imported', models.Bouwblok.objects.count())

    def process(self):
        # loads the csv
        if self.gob:
            for bb in uva2.process_csv(None, None, self.process_row, source=self.source, encoding='utf-8'):
                bb.save()
        else:
            for bb in uva2.process_uva2(self.uva_path, "BBK", self.process_row):
                bb.save()

        geo.process_shp(self.shp_path, "GBD_bouwblok.shp" if self.gob else "GBD_Bouwblok.shp", self.process_feature)

    def process_row(self, r):
        if self.gob:
            pk = r['identificatie']
            code = r['code']
            buurt_id = r['ligtIn:GBD.BRT.identificatie']
            ingang_cyclus = uva2.iso_datum(r['beginGeldigheid'])
            begin_geldigheid = uva2.iso_datum(r['beginGeldigheid'])
            einde_geldigheid = uva2.iso_datum(r['eindGeldigheid'])
        else:

            if not uva2.uva_geldig(r['BBKBRT/TijdvakRelatie/begindatumRelatie'],
                                   r['BBKBRT/TijdvakRelatie/einddatumRelatie']):
                return None

            pk = r['sleutelVerzendend']
            buurt_id = r['BBKBRT/BRT/sleutelVerzendend'] or None
            code = r['Bouwbloknummer']
            ingang_cyclus = uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'])
            begin_geldigheid = uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'])
            einde_geldigheid = uva2.uva_datum(
                r['TijdvakGeldigheid/einddatumTijdvakGeldigheid'])

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
        )

    def process_feature(self, feat):
        code = feat.get('CODE')
        try:
            bouwblok = models.Bouwblok.objects.get(code=code)
        except models.Bouwblok.DoesNotExist:
            log.warning("""
            Bouwblok/SHP {} code of non-existing bouwblok; skipping
            """.format(code))
            return

        bouwblok.geometrie = geo.get_multipoly(feat.geom.wkt)

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


class ImportWplTask(batch.BasicTask):
    name = "Import WPL"

    def __init__(self, path, gob):
        self.gob = gob
        self.path = path
        self.gemeentes = set()

    def before(self):
        self.gemeentes = set(
            models.Gemeente.objects.values_list("pk", flat=True))

    def after(self):
        self.gemeentes.clear()

    def process(self):

        if self.gob:
            source = os.path.join(self.path, 'BAG_woonplaats_Actueel.csv')
            woonplaatsen = uva2.process_csv(None, None, self.process_row, source=source, encoding='utf-8')
        else:
            woonplaatsen = uva2.process_uva2(self.path, "WPL", self.process_row)

        models.Woonplaats.objects.bulk_create(
            woonplaatsen, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if self.gob:
            pk = r['identificatie']
            # gemeente wordt niet geleverd, maar er is er maar een
            gemeente_id = next(iter(self.gemeentes))
            values = {
                'pk': pk,
                'landelijk_id': pk,
                'naam': r['naam'],
                'document_nummer': r['documentnummer'],
                'document_mutatie': uva2.iso_datum(r['documentdatum']),
                'naam_ptt': None,
                'vervallen': None,
                'gemeente_id': gemeente_id,
                'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
                'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
                'mutatie_gebruiker': None,
            }
        else:
            if not uva2.geldige_relaties(r, 'WPLGME'):
                return None

            pk = r['sleutelverzendend']
            gemeente_id = r['WPLGME/GME/sleutelVerzendend']

            values = {
                'pk': pk,
                'landelijk_id': r['Woonplaatsidentificatie'],
                'naam': r['Woonplaatsnaam'],
                'document_nummer': r['DocumentnummerMutatieWoonplaats'],
                'document_mutatie': uva2.uva_datum(
                    r['DocumentdatumMutatieWoonplaats']),
                'naam_ptt': r['WoonplaatsPTTSchrijfwijze'],
                'vervallen': uva2.uva_indicatie(r['Indicatie-vervallen']),
                'gemeente_id': gemeente_id,
                'begin_geldigheid': uva2.uva_datum(
                    r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
                'einde_geldigheid': uva2.uva_datum(
                    r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
                'mutatie_gebruiker': r['Mutatie-gebruiker'],
            }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        if gemeente_id not in self.gemeentes:
            log.warning("""
             Woonplaats {} references non-existing gemeente {}; skipping
             """.format(pk, gemeente_id))
            return None

        return models.Woonplaats(**values)


class ImportOpenbareRuimteTask(batch.BasicTask):
    name = "Import OPR - Openbare Ruimtes"

    def __init__(self, path, wkt_path, opr_beschrijving_path, gob):
        self.gob = gob
        self.path = path
        self.wkt_path = wkt_path
        self.opr_beschrijving_path = opr_beschrijving_path
        self.bronnen = set()
        self.statussen = set()
        self.woonplaatsen = set()
        self.landelijke_ids = dict()
        self.openbare_ruimtes = dict()
        self.omschijvingen = set()

    def store_opr_omschijving(self, row):
        return row['Openbareruimtenummer'], row['Omschrijving']

    def gob_store_opr_omschrijving(self, row):
        return row['identificatie'], row['beschrijving']

    def before(self):
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        if self.gob:
            self.statussen = dict(
                models.Status.objects.values_list("omschrijving", "pk"))
            self.types = dict([(t[1], t[0]) for t in models.OpenbareRuimte.TYPE_CHOICES])
        else:
            self.statussen = set(
                models.Status.objects.values_list("pk", flat=True))
        self.woonplaatsen = set(
            models.Woonplaats.objects.values_list("pk", flat=True))

        source = os.path.join(self.opr_beschrijving_path, 'BAG_openbare_ruimte_beschrijving_Actueel.csv' if self.gob else 'OPR_beschrijving.csv')

        self.omschrijvingen = dict(
            uva2.process_csv(
                None,
                None,
                self.gob_store_opr_omschrijving if self.gob else self.store_opr_omschijving,
                quotechar='"' if self.gob else '$', source=source, encoding='utf-8')
        )

    def after(self):
        self.bronnen.clear()
        self.statussen.clear()
        self.woonplaatsen.clear()
        self.landelijke_ids.clear()
        self.openbare_ruimtes.clear()
        if self.gob:
            self.types.clear()

    def process(self):
        if not self.gob:
            self.landelijke_ids = uva2.read_landelijk_id_mapping(self.path, "OPR")

        if self.gob:
            source = os.path.join(self.path, 'BAG_openbare_ruimte_Actueel.csv')
            self.openbare_ruimtes = dict(
                uva2.process_csv(None, None, self.process_row, source=source, encoding='utf-8'))

        else:
            self.openbare_ruimtes = dict(
                uva2.process_uva2(self.path, "OPR", self.process_row))

        if not self.gob:
            geo.process_wkt(
                self.wkt_path, "BAG_OPENBARERUIMTE_GEOMETRIE.dat",
                self.process_wkt_row)

        models.OpenbareRuimte.objects.bulk_create(
            self.openbare_ruimtes.values(), batch_size=database.BATCH_SIZE)

        validate_geometry(models.OpenbareRuimte)

    def process_row(self, r):
        if self.gob:
            pk = landelijk_id = r['identificatie']
            type = self.types.get(r['type'])
            if type  is None:
                log.error(f"OpenbareRuimte {pk} has invalid type {r['type']}; skipping")
                return None

            status = r['status']
            status_id = self.statussen.get(status)
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
                'status_id': status_id,
                'document_nummer': r['documentnummer'],
                'document_mutatie': uva2.iso_datum(r['documentdatum']),
                # 'straat_nummer': None,
                'naam_nen': naam_nen,
                # 'naam_ptt': None,
                # 'vervallen': None,  # TODO: ? Perhaps if daterange not geldig
                'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
                'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
                # 'mutatie_gebruiker': None,
                'geometrie': geometrie
            }
        else:
            if not uva2.geldig_tijdvak(r):
                return None

            if not uva2.geldige_relaties(r, 'OPRBRN', 'OPRSTS', 'OPRWPL'):
                return None

            pk = r['sleutelVerzendend']
            bron_id = r['OPRBRN/BRN/Code'] or None
            status_id = r['OPRSTS/STS/Code'] or None
            woonplaats_id = r['OPRWPL/WPL/sleutelVerzendend'] or None
            landelijk_id = self.landelijke_ids.get(pk)

            if not landelijk_id:
                log.error("""
                OpenbareRuimte {} references non-existing landelijk_id {}; skipping
                """.format(pk, pk))
                return

            if status_id not in self.statussen:
                log.warning("""
                    OpenbareRuimte {} references non-existing status {}; ignoring
                    """.format(pk, status_id))
                status_id = None

            if bron_id and bron_id not in self.bronnen:
                log.warning("""
                OpenbareRuimte {} references non-existing bron {}; ignoring
                """.format(pk, bron_id))
                bron_id = None

            values = {
                'pk': pk,
                'landelijk_id': landelijk_id,
                'type': r['TypeOpenbareRuimteDomein'],
                'naam': r['NaamOpenbareRuimte'],
                'code': r['Straatcode'],
                'document_nummer': r['DocumentnummerMutatieOpenbareRuimte'],
                'document_mutatie': uva2.uva_datum(r['DocumentdatumMutatieOpenbareRuimte']),
                'straat_nummer': r['Straatnummer'],
                'naam_nen': r['StraatnaamNENSchrijfwijze'],
                'naam_ptt': r['StraatnaamPTTSchrijfwijze'],
                'vervallen': uva2.uva_indicatie(r['Indicatie-vervallen']),
                'bron_id': bron_id,
                'status_id': status_id,
                'woonplaats_id': woonplaats_id,
                'begin_geldigheid': uva2.uva_datum(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
                'einde_geldigheid': uva2.uva_datum(r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
                'mutatie_gebruiker': r['Mutatie-gebruiker'],
            }

        if not uva2.datum_geldig(values['begin_geldigheid'], values['einde_geldigheid']):
            return None

        if values['woonplaats_id'] not in self.woonplaatsen:
            log.warning("""
            OpenbareRuimte {} references non-existing woonplaats {}; skipping
            """.format(pk, woonplaats_id))
            return None

        if landelijk_id:
            omschrijving = self.omschrijvingen.get(landelijk_id, None)
            values['omschrijving'] = omschrijving

        return pk, models.OpenbareRuimte(**values)

    def process_wkt_row(self, wkt_id, geometrie):
        key = '0' + wkt_id
        if key not in self.openbare_ruimtes:
            log.warning("""
            OpenbareRuimte/WKT {} references non-existing openbare ruimte {};
            skipping """.format(wkt_id, key))
            return

        self.openbare_ruimtes[key].geometrie = geo.get_multipoly(geometrie)


class SetHoofdAdres(batch.BasicTask):
    name = "set hoofdadressen"
    dataset_id = 'BAG'

    def __init__(self, path):

        self.path = path
        self.ligplaatsen = set()
        self.standplaatsen = set()
        self.verblijfsobjecten = set()
        self.nummeraanduidingen = set()

    def before(self):
        self.ligplaatsen = frozenset(
            models.Ligplaats.objects.values_list("pk", flat=True))

        self.standplaatsen = frozenset(
            models.Standplaats.objects.values_list("pk", flat=True))

        self.verblijfsobjecten = frozenset(
            models.Verblijfsobject.objects.values_list("pk", flat=True))

        self.nummeraanduidingen = frozenset(
            models.Nummeraanduiding.objects.values_list("pk", flat=True))

    def after(self):
        del self.ligplaatsen
        del self.standplaatsen
        del self.verblijfsobjecten
        del self.nummeraanduidingen

    def process(self):

        list(uva2.process_uva2(self.path, "NUMLIGHFD", self.process_numlig_row))
        list(uva2.process_uva2(self.path, "NUMSTAHFD", self.process_numsta_row))
        list(uva2.process_uva2(self.path, "NUMVBOHFD", self.process_numvbo_row))
        list(uva2.process_uva2(self.path, "NUMVBONVN", self.process_numvbonvn_row))

    def process_numlig_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMLIGHFD'):
            return

        pk = r['sleutelVerzendend']
        ligplaats_id = r['NUMLIGHFD/LIG/sleutelVerzendend']
        if ligplaats_id not in self.ligplaatsen:
            log.warning('Num-Lig-Hfd {} references non-existing ligplaats {}; skipping'.format(pk, ligplaats_id))
            return None

        nummeraanduiding_id = r['IdentificatiecodeNummeraanduiding']
        if nummeraanduiding_id not in self.nummeraanduidingen:
            log.warning(
                'Num-Lig-Hfd {} references non-existing nummeraanduiding {}; skipping'.format(pk, nummeraanduiding_id))
            return None

        nummeraanduiding = models.Nummeraanduiding.objects.get(pk=nummeraanduiding_id)
        nummeraanduiding.ligplaats_id = ligplaats_id
        nummeraanduiding.hoofdadres = True
        nummeraanduiding.save()

    def process_numsta_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMSTAHFD'):
            return

        pk = r['sleutelVerzendend']
        standplaats_id = r['NUMSTAHFD/STA/sleutelVerzendend']
        if standplaats_id not in self.standplaatsen:
            log.warning('Num-Sta-Hfd {} references non-existing standplaats {}; skipping'.format(pk, standplaats_id))
            return None

        nummeraanduiding_id = r['IdentificatiecodeNummeraanduiding']
        if nummeraanduiding_id not in self.nummeraanduidingen:
            log.warning(
                'Num-Sta-Hfd {} references non-existing nummeraanduiding {}; skipping'.format(pk, nummeraanduiding_id))
            return None

        nummeraanduiding = models.Nummeraanduiding.objects.get(id=nummeraanduiding_id)
        nummeraanduiding.standplaats_id = standplaats_id
        nummeraanduiding.hoofdadres = True
        nummeraanduiding.save()

    def process_numvbo_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBOHFD'):
            return

        pk = r['sleutelVerzendend']
        vbo_id = r['NUMVBOHFD/VBO/sleutelVerzendend']
        if vbo_id not in self.verblijfsobjecten:
            log.warning('Num-Vbo-Hfd {} references non-existing verblijfsobject {}; skipping'.format(pk, vbo_id))
            return None

        nummeraanduiding_id = r['IdentificatiecodeNummeraanduiding']
        if nummeraanduiding_id not in self.nummeraanduidingen:
            log.warning(
                'Num-Vbo-Hfd {} references non-existing nummeraanduiding {}; skipping'.format(pk, nummeraanduiding_id))
            return None

        nummeraanduiding = models.Nummeraanduiding.objects.get(id=nummeraanduiding_id)
        nummeraanduiding.verblijfsobject_id = vbo_id
        nummeraanduiding.hoofdadres = True
        nummeraanduiding.save()

    def process_numvbonvn_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBONVN'):
            return

        pk = r['sleutelVerzendend']
        vbo_id = r['NUMVBONVN/sleutelVerzendend']
        if vbo_id not in self.verblijfsobjecten:
            log.warning('Num-Vbo-Nvn {} references non-existing verblijfsobject {}; skipping'.format(pk, vbo_id))
            return None

        nummeraanduiding_id = r['IdentificatiecodeNummeraanduiding']
        if nummeraanduiding_id not in self.nummeraanduidingen:
            log.warning(
                'Num-Vbo-Nvn {} references non-existing nummeraanduiding {}; skipping'.format(pk, nummeraanduiding_id))
            return None

        nummeraanduiding = models.Nummeraanduiding.objects.get(id=nummeraanduiding_id)
        nummeraanduiding.verblijfsobject_id = vbo_id
        nummeraanduiding.hoofdadres = False
        nummeraanduiding.save()


class ImportNumTask(batch.BasicTask, metadata.UpdateDatasetMixin):
    name = "Import NUM"
    dataset_id = 'BAG'

    def __init__(self, path):
        self.path = path
        self.bronnen = set()
        self.statussen = set()
        self.openbare_ruimtes = set()
        self.landelijke_ids = dict()

    def before(self):
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        self.statussen = set(
            models.Status.objects.values_list("pk", flat=True))

        self.openbare_ruimtes = set(
            models.OpenbareRuimte.objects.values_list("pk", flat=True))

    def after(self):
        self.bronnen.clear()
        self.statussen.clear()
        self.openbare_ruimtes.clear()

        self.update_metadata_uva2(self.path, 'NUM')

        log.info('%d Nummeraanduiding Imported', models.Nummeraanduiding.objects.count())

    def process(self):

        self.landelijke_ids = uva2.read_landelijk_id_mapping(self.path, "NUM")
        # NOTE generator!
        nummeraanduidingen = uva2.process_uva2(self.path, "NUM", self.process_num_row)

        models.Nummeraanduiding.objects.bulk_create(
            nummeraanduidingen, batch_size=database.BATCH_SIZE)

    def process_num_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return None

        if not uva2.geldige_relaties(r, 'NUMBRN', 'NUMSTS', 'NUMOPR'):
            return None

        pk = r['sleutelVerzendend']
        bron_id = r['NUMBRN/BRN/Code'] or None
        status_id = r['NUMSTS/STS/Code'] or None
        openbare_ruimte_id = r['NUMOPR/OPR/sleutelVerzendend'] or None
        landelijk_id = self.landelijke_ids.get(
            r['IdentificatiecodeNummeraanduiding'])

        if not landelijk_id:
            log.error('Nummeraanduiding {} references non-existing landelijk_id {}; skipping'.format(pk, landelijk_id))
            return

        if bron_id and bron_id not in self.bronnen:
            log.warning('Nummeraanduiding {} references non-existing bron {}; ignoring'.format(pk, bron_id))
            bron_id = None

        if status_id not in self.statussen:
            log.warning('Nummeraanduiding {} references non-existing status {}; ignoring'.format(pk, status_id))
            status_id = None

        if openbare_ruimte_id not in self.openbare_ruimtes:
            log.warning('Nummeraanduiding {} references non-existing openbare ruimte {}; skipping'
                        .format(pk, openbare_ruimte_id))
            return None

        return models.Nummeraanduiding(
            pk=pk,
            landelijk_id=landelijk_id,
            huisnummer=r['Huisnummer'],
            huisletter=r['Huisletter'],
            huisnummer_toevoeging=r['Huisnummertoevoeging'],
            postcode=r['Postcode'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieNummeraanduiding']),
            document_nummer=r['DocumentnummerMutatieNummeraanduiding'],
            type=r['TypeAdresseerbaarObjectDomein'],
            adres_nummer=r['Adresnummer'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron_id=bron_id,
            status_id=status_id,
            openbare_ruimte_id=openbare_ruimte_id,
            begin_geldigheid=uva2.uva_datum(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
            einde_geldigheid=uva2.uva_datum(r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
            mutatie_gebruiker=r['Mutatie-gebruiker'],
        )


class ImportLigTask(batch.BasicTask):
    name = "Import LIG"

    def __init__(self, bag_path, wkt_path, gob):
        self.gob = gob
        self.bag_path = bag_path
        self.wkt_path = wkt_path
        self.bronnen = set()
        self.statussen = set()
        self.buurten = set()
        self.landelijke_ids = dict()

        self.ligplaatsen = dict()

    def before(self):
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        if self.gob:
            self.statussen = dict(
                models.Status.objects.values_list("omschrijving", "pk"))
        else:
            self.statussen = set(
                models.Status.objects.values_list("pk", flat=True))

        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))

    def after(self):
        self.bronnen.clear()
        self.statussen.clear()
        self.buurten.clear()

        self.ligplaatsen.clear()

    def process(self):
        if not self.gob:
            self.landelijke_ids = uva2.read_landelijk_id_mapping(self.bag_path, "LIG")
            self.ligplaatsen = dict(uva2.process_uva2(self.bag_path, "LIG", self.process_row))
            geo.process_wkt(self.wkt_path, 'BAG_LIGPLAATS_GEOMETRIE.dat', self.process_wkt_row)
        else:
            source = os.path.join(self.bag_path, 'BAG_ligplaats_Actueel.csv')
            self.ligplaatsen = dict(uva2.process_csv(None, None, self.process_row, source=source, encoding='utf-8'))

        models.Ligplaats.objects.bulk_create(self.ligplaatsen.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if self.gob:
            pk = landelijk_id = r['identificatie']
            status = r['status']
            status_id = self.statussen.get(status)
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
                'status_id': status_id,
                'buurt_id': r['ligtIn:GBD.BRT.identificatie'] or None,
                'begin_geldigheid': uva2.iso_datum_tijd(r['beginGeldigheid']),
                'einde_geldigheid': uva2.iso_datum_tijd(r['eindGeldigheid']),
                # 'mutatie_gebruiker': None,
                'indicatie_in_onderzoek': uva2.get_janee_boolean(r['aanduidingInOnderzoek']),
                'indicatie_geconstateerd': uva2.get_janee_boolean(r['geconstateerd']),
                'geometrie': geometrie
            }
        else:

            if not uva2.geldig_tijdvak(r):
                return None

            if not uva2.geldige_relaties(r, 'LIGBRN', 'LIGSTS', 'LIGBRT'):
                return None

            pk = r['sleutelverzendend']
            bron_id = r['LIGBRN/BRN/Code'] or None
            status_id = r['LIGSTS/STS/Code'] or None
            landelijk_id = self.landelijke_ids.get(r['Ligplaatsidentificatie'])

            if not landelijk_id:
                log.error('Ligplaats {} references non-existing landelijk_id {}; skipping'.format(pk, landelijk_id))
                return

            if bron_id and bron_id not in self.bronnen:
                log.warning('Ligplaats {} references non-existing bron {}; ignoring'.format(pk, bron_id))
                bron_id = None

            if status_id and status_id not in self.statussen:
                log.warning('Ligplaats {} references non-existing status {}; ignoring'.format(pk, status_id))
                status_id = None

            values = {
                'pk': pk,
                'landelijk_id': landelijk_id,
                'vervallen': uva2.uva_indicatie(r['Indicatie-vervallen']),
                'document_nummer': r['DocumentnummerMutatieLigplaats'],
                'document_mutatie': uva2.uva_datum(r['DocumentdatumMutatieLigplaats']),
                'bron_id': bron_id,
                'status_id': status_id,
                'buurt_id': r['LIGBRT/BRT/sleutelVerzendend'] or None,
                'begin_geldigheid': uva2.uva_datum(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
                'einde_geldigheid': uva2.uva_datum(r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
                'mutatie_gebruiker': r['Mutatie-gebruiker'],
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
    name = "Import STA - Standplaatsen"

    def __init__(self, bag_path, wkt_path):
        self.bag_path = bag_path
        self.wkt_path = wkt_path
        self.bronnen = set()
        self.statussen = set()
        self.buurten = set()
        self.landelijke_ids = dict()

    def before(self):
        log.info('Importing standplaatsen')
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        self.statussen = set(models.Status.objects.values_list("pk", flat=True))
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))

    def after(self):
        self.bronnen.clear()
        self.statussen.clear()
        self.buurten.clear()

        validate_geometry(models.Standplaats)

        assert models.Standplaats.objects.filter(
            geometrie__isnull=True).count() == 0, "Standplaats zonder geometrie!"

        log.info(
            '%s Standplaatsen',
            models.Standplaats.objects.filter(
                geometrie__isnull=True).count())

    def process(self):
        self.landelijke_ids = uva2.read_landelijk_id_mapping(self.bag_path, "STA")
        standplaatsen = uva2.process_uva2(self.bag_path, "STA", self.process_row)

        models.Standplaats.objects.bulk_create(standplaatsen, batch_size=database.BATCH_SIZE)

        geo.process_wkt(self.wkt_path, "BAG_STANDPLAATS_GEOMETRIE.dat", self.process_wkt_row)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'STABRN', 'STASTS', 'STABRT'):
            return

        pk = r['sleutelverzendend']
        bron_id = r['STABRN/BRN/Code'] or None
        status_id = r['STASTS/STS/Code'] or None
        buurt_id = r['STABRT/BRT/sleutelVerzendend'] or None
        landelijk_id = self.landelijke_ids.get(r['Standplaatsidentificatie'])

        if not landelijk_id:
            log.error('Standplaats {} references non-existing landelijk_id {}; skipping'.format(pk, landelijk_id))
            return

        if bron_id and bron_id not in self.bronnen:
            log.warning('Standplaats {} references non-existing bron {}; ignoring'.format(pk, bron_id))
            bron_id = None

        if status_id and status_id not in self.statussen:
            log.warning('Standplaats {} references non-existing status {}; ignoring'.format(pk, status_id))
            status_id = None

        if buurt_id and buurt_id not in self.buurten:
            log.warning('Standplaats {} references non-existing buurt {}; ignoring'.format(pk, status_id))
            buurt_id = None

        return models.Standplaats(
            pk=pk,
            landelijk_id=landelijk_id,
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieStandplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieStandplaats']),
            bron_id=bron_id,
            status_id=status_id,
            buurt_id=buurt_id,
            begin_geldigheid=uva2.uva_datum(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
            einde_geldigheid=uva2.uva_datum(r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
            mutatie_gebruiker=r['Mutatie-gebruiker'],
        )

    def process_wkt_row(self, wkt_id, geometrie):
        key = '0' + wkt_id
        try:
            standplaats = models.Standplaats.objects.get(id=key)
        except models.Standplaats.DoesNotExist:
            log.warning('Standplaats/WKT {} references non-existing standplaats {}; skipping'.format(wkt_id, key))
            return

        standplaats.geometrie = geometrie
        return standplaats.save()


class ImportVboTask(batch.BasicTask):
    name = "Import VBO - Verblijfsobjecten"

    def __init__(self, path):
        self.path = path
        self.redenen_afvoer = set()
        self.redenen_opvoer = set()
        self.bronnen = set()
        self.eigendomsverhoudingen = set()
        self.financieringswijzes = set()
        self.gebruik = set()
        self.locaties_ingang = set()
        self.liggingen = set()
        self.toegang = set()
        self.statussen = set()
        self.buurten = set()
        self.landelijke_ids = dict()

    def before(self):
        self.redenen_afvoer = set(models.RedenAfvoer.objects.values_list("pk", flat=True))
        self.redenen_opvoer = set(models.RedenOpvoer.objects.values_list("pk", flat=True))
        self.bronnen = set(models.Bron.objects.values_list("pk", flat=True))
        self.eigendomsverhoudingen = set(models.Eigendomsverhouding.objects.values_list("pk", flat=True))
        self.financieringswijzes = set(models.Financieringswijze.objects.values_list("pk", flat=True))
        self.gebruik = set(models.Gebruik.objects.values_list("pk", flat=True))
        self.locaties_ingang = set(models.LocatieIngang.objects.values_list("pk", flat=True))
        self.liggingen = set(models.Ligging.objects.values_list("pk", flat=True))
        self.toegang = set(models.Toegang.objects.values_list("pk", flat=True))
        self.statussen = set(models.Status.objects.values_list("pk", flat=True))
        self.buurten = set(models.Buurt.objects.values_list("pk", flat=True))

    def after(self):
        self.redenen_afvoer.clear()
        self.redenen_opvoer.clear()
        self.bronnen.clear()
        self.eigendomsverhoudingen.clear()
        self.financieringswijzes.clear()
        self.gebruik.clear()
        self.locaties_ingang.clear()
        self.liggingen.clear()
        self.toegang.clear()
        self.statussen.clear()
        self.buurten.clear()

        log.info('%d Verblijfsobjecten Imported', models.Verblijfsobject.objects.count())

    def process(self):
        self.landelijke_ids = uva2.read_landelijk_id_mapping(self.path, "VBO")

        verblijfsobjecten = uva2.process_uva2(self.path, "VBO", self.process_row)

        models.Verblijfsobject.objects.bulk_create(verblijfsobjecten, batch_size=database.BATCH_SIZE)

        validate_geometry(models.Verblijfsobject)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(
                r, 'VBOAVR', 'VBOOVR', 'VBOBRN', 'VBOEGM',
                'VBOFNG', 'VBOGBK', 'VBOLOC', 'VBOLGG',
                'VBOMNT', 'VBOTGG', 'VBOOVR', 'VBOSTS',
                'VBOBRT'):
            return

        x = r['X-Coordinaat']
        y = r['Y-Coordinaat']

        if x and y:
            geo1 = Point(int(x), int(y))
        else:
            geo1 = None

        pk = r['sleutelverzendend']
        reden_afvoer_id = r['VBOAVR/AVR/Code'] or None
        reden_opvoer_id = r['VBOOVR/OVR/Code'] or None
        bron_id = r['VBOBRN/BRN/Code'] or None
        eigendomsverhouding_id = r['VBOEGM/EGM/Code'] or None
        financieringswijze_id = r['VBOFNG/FNG/Code'] or None
        gebruik_id = r['VBOGBK/GBK/Code'] or None
        locatie_ingang_id = r['VBOLOC/LOC/Code'] or None
        ligging_id = r['VBOLGG/LGG/Code'] or None
        toegang_id = r['VBOTGG/TGG/Code'] or None
        status_id = r['VBOSTS/STS/Code'] or None
        buurt_id = r['VBOBRT/BRT/sleutelVerzendend'] or None
        landelijk_id = self.landelijke_ids.get(r['Verblijfsobjectidentificatie'])

        if not landelijk_id:
            log.error('Verblijfsobject {} references non-existing landelijk_id {}; skipping'.format(pk, landelijk_id))
            return

        if reden_afvoer_id and reden_afvoer_id not in self.redenen_afvoer:
            log.warning('Verblijfsobject {} references non-existing reden afvoer {}; ignoring'.format(pk, bron_id))
            reden_afvoer_id = None

        if reden_opvoer_id and reden_opvoer_id not in self.redenen_opvoer:
            log.warning('Verblijfsobject {} references non-existing reden opvoer {}; ignoring'.format(pk, bron_id))
            reden_opvoer_id = None

        if bron_id and bron_id not in self.bronnen:
            log.warning('Verblijfsobject {} references non-existing bron {}; ignoring'.format(pk, bron_id))
            bron_id = None

        if eigendomsverhouding_id and eigendomsverhouding_id not in self.eigendomsverhoudingen:
            log.warning(
                'Verblijfsobject {} references non-existing eigendomsverhouding {}; ignoring'.format(
                    pk, eigendomsverhouding_id))

            eigendomsverhouding_id = None

        if financieringswijze_id and financieringswijze_id not in self.financieringswijzes:
            log.warning(
                'Verblijfsobject {} references non-existing financieringswijze {}; ignoring'.format(
                    pk, financieringswijze_id))

            financieringswijze_id = None

        if gebruik_id and gebruik_id not in self.gebruik:
            log.warning('Verblijfsobject {} references non-existing gebruik {}; ignoring'.format(pk, gebruik_id))
            gebruik_id = None

        if locatie_ingang_id and locatie_ingang_id not in self.locaties_ingang:
            log.warning(
                'Verblijfsobject {} references non-existing locatie ingang {}; ignoring'.format(pk, locatie_ingang_id))
            locatie_ingang_id = None

        if ligging_id and ligging_id not in self.liggingen:
            log.warning('Verblijfsobject {} references non-existing ligging {}; ignoring'.format(pk, ligging_id))
            ligging_id = None

        if toegang_id and toegang_id not in self.toegang:
            log.warning('Verblijfsobject {} references non-existing toegang {}; ignoring'.format(pk, toegang_id))
            toegang_id = None

        if status_id and status_id not in self.statussen:
            log.warning('Verblijfsobject {} references non-existing status {}; ignoring'.format(pk, status_id))
            status_id = None

        if buurt_id and buurt_id not in self.buurten:
            log.warning('Verblijfsobject {} references non-existing bron {}; ignoring'.format(pk, buurt_id))
            buurt_id = None

        return models.Verblijfsobject(
            pk=pk,
            landelijk_id=landelijk_id,
            geometrie=geo1,
            oppervlakte=uva2.uva_nummer(r['OppervlakteVerblijfsobject']),
            document_mutatie=uva2.uva_datum(
                r['DocumentdatumMutatieVerblijfsobject']),
            document_nummer=(r['DocumentnummerMutatieVerblijfsobject']),
            bouwlaag_toegang=uva2.uva_nummer(r['Bouwlaagtoegang']),
            status_coordinaat_code=(r['StatusCoordinaatDomein']),
            status_coordinaat_omschrijving=(r['OmschrijvingCoordinaatDomein']),
            verhuurbare_eenheden=r['AantalVerhuurbareEenheden'] or None,
            bouwlagen=uva2.uva_nummer(r['AantalBouwlagen']),
            type_woonobject_code=(r['TypeWoonobjectDomein']),
            type_woonobject_omschrijving=(
                r['OmschrijvingTypeWoonobjectDomein']),
            woningvoorraad=uva2.uva_indicatie(r['IndicatieWoningvoorraad']),
            aantal_kamers=uva2.uva_nummer(r['AantalKamers']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            reden_afvoer_id=reden_afvoer_id,
            reden_opvoer_id=reden_opvoer_id,
            bron_id=bron_id,
            eigendomsverhouding_id=eigendomsverhouding_id,
            financieringswijze_id=financieringswijze_id,
            gebruik_id=gebruik_id,
            locatie_ingang_id=locatie_ingang_id,
            ligging_id=ligging_id,
            # ?=(r['VBOMNT/MNT/Code']),
            toegang_id=toegang_id,
            # ?=(r['VBOOVR/OVR/Code']),
            status_id=status_id,
            buurt_id=buurt_id,
            begin_geldigheid=uva2.uva_datum(
                r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
            einde_geldigheid=uva2.uva_datum(
                r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
            mutatie_gebruiker=r['Mutatie-gebruiker'],
        )


class ImportPandTask(batch.BasicTask):
    name = "Import PND"

    def __init__(self, bag_path, wkt_path):
        self.wkt_path = wkt_path
        self.bag_path = bag_path
        self.statussen = set()
        self.bouwblokken = set()
        self.panden = dict()
        self.landelijke_ids = dict()

    def before(self):
        self.statussen = set(models.Status.objects.values_list("pk", flat=True))
        self.bouwblokken = set(models.Bouwblok.objects.values_list("pk", flat=True))

    def after(self):
        self.statussen.clear()
        self.panden.clear()
        self.bouwblokken.clear()
        self.landelijke_ids.clear()

    def process(self):
        self.landelijke_ids = uva2.read_landelijk_id_mapping(self.bag_path, "PND")
        self.panden = dict(uva2.process_uva2(self.bag_path, "PND", self.process_row))

        geo.process_wkt(self.wkt_path, "BAG_PAND_GEOMETRIE.dat", self.process_wkt_row)

        models.Pand.objects.bulk_create(self.panden.values(), batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDSTS', 'PNDBBK'):
            return

        pk = r['sleutelverzendend']
        status_id = r['PNDSTS/STS/Code'] or None
        bbk_id = r['PNDBBK/BBK/sleutelVerzendend'] or None
        landelijk_id = self.landelijke_ids.get(r['Pandidentificatie'])

        if not landelijk_id:
            log.error('Pand {} references non-existing landelijk_id {}; skipping'.format(pk, landelijk_id))
            return

        if status_id and status_id not in self.statussen:
            log.warning('Pand {} references non-existing status {}; ignoring'.format(pk, status_id))
            status_id = None

        if bbk_id and bbk_id not in self.bouwblokken:
            log.warning('Pand {} references non-existing bouwblok {}; ignoring'.format(pk, bbk_id))
            bbk_id = None

        return pk, models.Pand(
            pk=pk,
            landelijk_id=landelijk_id,
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatiePand']),
            document_nummer=(r['DocumentnummerMutatiePand']),
            bouwjaar=uva2.uva_nummer(r['OorspronkelijkBouwjaarPand']),
            laagste_bouwlaag=uva2.uva_nummer(r['LaagsteBouwlaag']),
            hoogste_bouwlaag=uva2.uva_nummer(r['HoogsteBouwlaag']),
            pandnummer=(r['Pandnummer']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            status_id=status_id,
            begin_geldigheid=uva2.uva_datum(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid']),
            einde_geldigheid=uva2.uva_datum(r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']),
            mutatie_gebruiker=r['Mutatie-gebruiker'],
            bouwblok_id=bbk_id,
        )

    def process_wkt_row(self, wkt_id, geometrie):
        key = '0' + wkt_id
        if key not in self.panden:
            log.warning('Pand/WKT {} references non-existing pand {}; skipping'.format(wkt_id, key))
            return

        self.panden[key].geometrie = geometrie


class ImportPandVboTask(batch.BasicTask):
    name = "Import PNDVBO - Pand-Verblijfsobject relatie"

    def __init__(self, path):
        self.path = path
        self.panden = set()
        self.vbos = set()

    def before(self):

        self.panden = frozenset(
            models.Pand.objects.values_list("pk", flat=True))

        self.vbos = frozenset(
            models.Verblijfsobject.objects.values_list("pk", flat=True))

    def after(self):
        self.panden = None
        self.vbos = None
        log.info('%d VBO-PAND relaties', models.VerblijfsobjectPandRelatie.objects.count())

    def process(self):
        relaties = frozenset(
            uva2.process_uva2(self.path, "PNDVBO", self.process_row))

        models.VerblijfsobjectPandRelatie.objects.bulk_create(
            relaties, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return None

        if not uva2.geldige_relaties(r, 'PNDVBO'):
            return None

        pand_id = r['sleutelverzendend']
        vbo_id = r['PNDVBO/VBO/sleutelVerzendend']

        if vbo_id not in self.vbos:
            log.warning('Pand/VBO {} references non-existing verblijfsobject {}; skipping'.format(pand_id, vbo_id))
            return None

        if pand_id not in self.panden:
            log.warning('Pand/VBO {} references non-existing pand {}; skipping'.format(pand_id, pand_id))
            return None

        return models.VerblijfsobjectPandRelatie(
            verblijfsobject_id=vbo_id,
            pand_id=pand_id,
        )


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
        prefetch_related('verblijfsobject__status').\
        prefetch_related('standplaats').\
        prefetch_related('standplaats__status').\
        prefetch_related('ligplaats').\
        prefetch_related('ligplaats__status').\
        prefetch_related('status').\
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

    def __init__(self, shp_path, gob):
        self.gob = gob
        self.shp_path = shp_path
        self.stadsdelen = dict()

    def before(self):
        self.stadsdelen = dict(
            models.Stadsdeel.objects.values_list("code", "id"))

    def after(self):
        self.stadsdelen.clear()
        validate_geometry(models.Buurtcombinatie)

    def process(self):
        shp_file = "GBD_wijk.shp" if self.gob else "GBD_Buurtcombinatie.shp"
        geo.process_shp(
            self.shp_path, shp_file, self.process_feature)

    def process_feature(self, feat):

        if self.gob:
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
        else:
            vollcode = feat.get('VOLLCODE')

            wijk = models.Buurtcombinatie(
                id=str(int(feat.get('ID'))),
                naam=feat.get('NAAM'),
                code=feat.get('CODE'),
                vollcode=vollcode,
                brondocument_naam=feat.get('DOCNR'),
                brondocument_datum=feat.get('DOCDATUM'),
                ingang_cyclus=feat.get('INGSDATUM'),
                geometrie=geo.get_multipoly(feat.geom.wkt),
                stadsdeel_id=self.stadsdelen.get(vollcode[0]),
                begin_geldigheid=feat.get('INGSDATUM'),
                einde_geldigheid=feat.get('EINDDATUM'),
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
    assert count == 0


class ImportGebiedsgerichtwerkenTask(batch.BasicTask):
    """
    layer.fields:

    ['naam', 'code', 'sdl_code', ...]
    TODO : In GOB import the GBD_ggw_gebied has also a 14 digit ID . Do we need this ID in the current API ?
    """

    name = "Import GBD Gebiedsgerichtwerken"

    def __init__(self, shp_path, gob):
        self.gob = gob
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
        shp_file = "GBD_ggw_gebied.shp" if self.gob else "GBD_gebiedsgerichtwerken.shp"
        geo.process_shp(
            self.shp_path, shp_file,
            self.process_feature)

    def process_feature(self, feat):
        if self.gob:
            sdl = feat.get('sdl_code')
            code = feat.get('code')
            naam = feat.get('naam')
        else:
            sdl = feat.get('STADSDEEL')
            code = feat.get('CODE')
            naam = feat.get('NAAM')

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

    def __init__(self, shp_path, gob):
        self.gob = gob
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
        shp_file = "GBD_ggw_praktijkgebied.shp" if self.gob else "GBD_gebiedsgerichtwerken_praktijk.shp"
        geo.process_shp(
            self.shp_path, shp_file,
            self.process_feature)

    def process_feature(self, feat):
        naam = feat.get('naam' if self.gob else 'NAAM')

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


class DenormalizeIndicatieTask(batch.BasicTask):
    name = "Add indicatie to BAG vbo / standplaats / ligplaats data"

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        update_aot_sql = """
UPDATE {tablename} vbo
SET
    indicatie_geconstateerd = i.indicatie_geconstateerd,
    indicatie_in_onderzoek = i.indicatie_in_onderzoek
FROM (
    SELECT
        ind.landelijk_id,
        ind.indicatie_geconstateerd,
        ind.indicatie_in_onderzoek
    FROM bag_indicatieadresseerbaarobject ind
    ) i
WHERE i.landelijk_id = vbo.landelijk_id

        """

        aot_tables = [
            'bag_verblijfsobject',
            'bag_ligplaats',
            'bag_standplaats'
        ]

        for aot in aot_tables:
            with connection.cursor() as c:
                c.execute(update_aot_sql.format(tablename=aot))


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
       WHERE num.hoofdadres
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
       WHERE num.hoofdadres AND num.ligplaats_id IS NOT NULL
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
       WHERE num.hoofdadres AND num.standplaats_id IS NOT NULL
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
        self.gob = kwargs.get('gob', False)
        if self.gob:
            gob_dir = settings.GOB_DIR
            self.gob_gebieden_path = os.path.join(gob_dir, 'gebieden/CSV_Actueel')
            self.gob_gebieden_shp_path = os.path.join(gob_dir, 'gebieden/SHP')
            self.gob_bag_path = os.path.join(gob_dir, 'bag/CSV_Actueel')

    def tasks(self):

        return [
            # no-dependencies.
            ImportIndicatieAOTTask(self.bag_path, self.gob),

            # ImportAvrTask(self.bag_path),
            # ImportOvrTask(self.bag_path),
 #           ImportBronTask(self.bag_path),  # Not needed in GOB
            # ImportEgmTask(self.bag_path),
            # ImportFngTask(self.bag_path),
            # ImportGbkTask(self.bag_path),
            # ImportLggTask(self.bag_path),
            # ImportLocTask(self.bag_path),
            # ImportTggTask(self.bag_path),
  #          ImportStatusTask(self.bag_path),  # TODO : hardcode in GOB import ?
#            ImportGmeTask(self.gebieden_path),  # TODO : Gemeente komt in GOB BRK
#            ImportWplTask(self.gob_bag_path if self.gob else self.bag_path, self.gob),
#            ImportSdlTask(self.gob_gebieden_path if self.gob else self.gebieden_path,
#                          self.gob_gebieden_shp_path if self.gob else self.gebieden_shp_path,
#                          self.gob),
#            ImportWijkTask(self.gob_gebieden_shp_path if self.gob else self.gebieden_shp_path, self.gob),

            # stadsdelen.
#            ImportGebiedsgerichtwerkenTask(self.gob_gebieden_shp_path if self.gob else self.gebieden_shp_path,
#                                            self.gob),
#            ImportGebiedsgerichtwerkenPraktijkgebiedenTask(
#                 self.gob_gebieden_shp_path if self.gob else self.gebieden_shp_path, self.gob),
            # # ImportGrootstedelijkgebiedTask(self.gebieden_shp_path),   # TODO : nog niet geleverd door GOB
            # # ImportUnescoTask(self.gebieden_shp_path),                 # TODO : nog niet geleverd door GOB
            # #
 #           ImportBuurtTask(self.gob_gebieden_path if self.gob else self.gebieden_path,
 #                           self.gob_gebieden_shp_path if self.gob else self.gebieden_shp_path,
 #                           self.gob),
            # # depends on buurten.
            # ImportBouwblokTask(self.gob_gebieden_path if self.gob else self.gebieden_path,
            #                    self.gob_gebieden_shp_path if self.gob else self.gebieden_shp_path,
            #                    self.gob),
            #
#            ImportOpenbareRuimteTask(
#                self.gob_bag_path if self.gob else self.bag_path,
#                self.bag_wkt_path,
#                self.gob_bag_path if self.gob else self.opr_beschrijving_path,
#                self.gob
#            ),

            ImportLigTask(self.gob_bag_path if self.gob else self.bag_path,
                          self.bag_wkt_path,
                          self.gob),
            # ImportStandplaatsenTask(self.bag_path, self.bag_wkt_path),
            # #
            # ImportPandTask(self.bag_path, self.bag_wkt_path),
            # #
            # ImportPandNaamTask(self.bag_path),
            #
            # # large. 500.000
            # ImportVboTask(self.bag_path),
            #
            # ImportGebruiksdoelenTask(self.bag_path),
            #
            # # large. 500.000
            # ImportNumTask(self.bag_path),
            #
            # # finising stuff.
            # SetHoofdAdres(self.bag_path),
            #
            #
            # # requires all vbo's to be there
            # ImportPandVboTask(self.bag_path),
            #
            # # some sql copying fields
            # DenormalizeDataTask(),
            # DenormalizeIndicatieTask(),
            #
            # # more denormalizeing sql
            # UpdateGebiedenAttributenTask(),
            # UpdateGrootstedelijkAttributenTask(),
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

# This seems not to be used  anywhere
# class ImportGebiedsgerichtwerkenPraktijkgebiedenJob(object):
#     name = "Delete and Fill the ggw praktijkgebieden "
#
#     def __init__(self):
#         diva = settings.DIVA_DIR
#         if not os.path.exists(diva):
#             raise ValueError("DIVA_DIR not found: {}".format(diva))
#         self.gebieden_shp_path = os.path.join(diva, 'gebieden_shp')
#
#     def tasks(self):
#         return [
#             ImportGebiedsgerichtwerkenPraktijkgebiedenTask(self.gebieden_shp_path)
#         ]
