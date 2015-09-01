from collections import OrderedDict
import logging

from django.contrib.gis.geos import Point

from atlas import models
from atlas_jobs import uva2
from atlas_jobs import batch

log = logging.getLogger(__name__)


class CodeOmschrijvingUvaTask(batch.AbstractUvaTask):
    model = None

    def execute(self):
        self.model.objects.all().delete()
        super().execute()

    def process_row(self, r):
        # noinspection PyCallingNonCallable
        self.create(self.model(
            pk=r['Code'],
            omschrijving=r['Omschrijving']
        ))


class ImportBrnTask(CodeOmschrijvingUvaTask):
    name = "import BRN"
    code = "BRN"
    model = models.Bron


class ImportAvrTask(CodeOmschrijvingUvaTask):
    name = "import AVR"
    code = "AVR"
    model = models.RedenAfvoer


class ImportStsTask(CodeOmschrijvingUvaTask):
    name = "import STS"
    code = "STS"
    model = models.Status


class ImportEgmTask(CodeOmschrijvingUvaTask):
    name = "import EGM"
    code = "EGM"
    model = models.Eigendomsverhouding


class ImportFngTask(CodeOmschrijvingUvaTask):
    name = "import FNG"
    code = "FNG"
    model = models.Financieringswijze


class ImportLggTask(CodeOmschrijvingUvaTask):
    name = "import LGG"
    code = "LGG"
    model = models.Ligging


class ImportGbkTask(CodeOmschrijvingUvaTask):
    name = "import GBK"
    code = "GBK"
    model = models.Gebruik


class ImportLocTask(CodeOmschrijvingUvaTask):
    name = "import LOC"
    code = "LOC"
    model = models.LocatieIngang


class ImportTggTask(CodeOmschrijvingUvaTask):
    name = "import TGG"
    code = "TGG"
    model = models.Toegang


class ImportGmeTask(batch.AbstractUvaTask):
    name = "import GME"
    code = "GME"

    def execute(self):
        models.Gemeente.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        self.create(models.Gemeente(
            pk=r['sleutelVerzendend'],
            code=r['Gemeentecode'],
            naam=r['Gemeentenaam'],
            verzorgingsgebied=uva2.uva_indicatie(r['IndicatieVerzorgingsgebied']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class ImportSdlTask(batch.AbstractUvaTask):
    name = "import SDL"
    code = "SDL"

    def execute(self):
        models.Stadsdeel.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['SDLGME/TijdvakRelatie/begindatumRelatie'],
                               r['SDLGME/TijdvakRelatie/einddatumRelatie']):
            return

        self.create(models.Stadsdeel(
            pk=r['sleutelVerzendend'],
            code=r['Stadsdeelcode'],
            naam=r['Stadsdeelnaam'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente=models.Gemeente.objects.get(pk=r['SDLGME/GME/sleutelVerzendend']),
        ))


class ImportBrtTask(batch.AbstractUvaTask):
    name = "import BRT"
    code = "BRT"

    def execute(self):
        models.Buurt.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.uva_geldig(r['TijdvakGeldigheid/begindatumTijdvakGeldigheid'],
                               r['TijdvakGeldigheid/einddatumTijdvakGeldigheid']):
            return

        if not uva2.uva_geldig(r['BRTSDL/TijdvakRelatie/begindatumRelatie'],
                               r['BRTSDL/TijdvakRelatie/einddatumRelatie']):
            return

        self.create(models.Buurt(
            pk=r['sleutelVerzendend'],
            code=r['Buurtcode'],
            naam=r['Buurtnaam'],
            stadsdeel=models.Stadsdeel.objects.get(pk=r['BRTSDL/SDL/sleutelVerzendend']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
        ))


class ImportWplTask(batch.AbstractUvaTask):
    name = "import WPL"
    code = "WPL"

    def execute(self):
        models.Woonplaats.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'WPLGME'):
            return

        self.create(models.Woonplaats(
            pk=r['sleutelverzendend'],
            code=r['Woonplaatsidentificatie'],
            naam=r['Woonplaatsnaam'],
            document_nummer=r['DocumentnummerMutatieWoonplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieWoonplaats']),
            naam_ptt=r['WoonplaatsPTTSchrijfwijze'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            gemeente_id=self.foreign_key_id(models.Gemeente, r['WPLGME/GME/sleutelVerzendend']),
        ))


class ImportOprTask(batch.AbstractUvaTask):
    name = "import OPR"
    code = "OPR"

    def execute(self):
        models.OpenbareRuimte.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'OPRBRN', 'OPRSTS', 'OPRWPL'):
            return

        self.create(models.OpenbareRuimte(
            pk=r['sleutelVerzendend'],
            type=r['TypeOpenbareRuimteDomein'],
            naam=r['NaamOpenbareRuimte'],
            code=r['Straatcode'],
            document_nummer=r['DocumentnummerMutatieOpenbareRuimte'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieOpenbareRuimte']),
            straat_nummer=r['Straatnummer'],
            naam_nen=r['StraatnaamNENSchrijfwijze'],
            naam_ptt=r['StraatnaamPTTSchrijfwijze'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron_id=self.foreign_key_id(models.Bron, r['OPRBRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['OPRSTS/STS/Code']),
            woonplaats_id=self.foreign_key_id(models.Woonplaats, r['OPRWPL/WPL/sleutelVerzendend']),
        ))


class ImportNumTask(batch.AbstractUvaTask):
    name = "import NUM"
    code = "NUM"

    def execute(self):
        models.Nummeraanduiding.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMBRN', 'NUMSTS', 'NUMOPR'):
            return

        self.create(models.Nummeraanduiding(
            pk=r['sleutelVerzendend'],
            code=r['IdentificatiecodeNummeraanduiding'],
            huisnummer=r['Huisnummer'],
            huisletter=r['Huisletter'],
            huisnummer_toevoeging=r['Huisnummertoevoeging'],
            postcode=r['Postcode'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieNummeraanduiding']),
            document_nummer=r['DocumentnummerMutatieNummeraanduiding'],
            type=r['TypeAdresseerbaarObjectDomein'],
            adres_nummer=r['Adresnummer'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            bron_id=self.foreign_key_id(models.Bron, r['NUMBRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['NUMSTS/STS/Code']),
            openbare_ruimte_id=self.foreign_key_id(models.OpenbareRuimte, r['NUMOPR/OPR/sleutelVerzendend']),
        ))


class ImportLigTask(batch.AbstractUvaTask):
    name = "import LIG"
    code = "LIG"

    def execute(self):
        models.Ligplaats.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'LIGBRN', 'LIGSTS', 'LIGBRT'):
            return

        self.create(models.Ligplaats(
            pk=r['sleutelverzendend'],
            identificatie=r['Ligplaatsidentificatie'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieLigplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieLigplaats']),
            bron_id=self.foreign_key_id(models.Bron, r['LIGBRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['LIGSTS/STS/Code']),
            buurt_id=self.foreign_key_id(models.Buurt, r['LIGBRT/BRT/sleutelVerzendend'])
        ))


class ImportNumLigHfdTask(batch.AbstractUvaTask):
    name = "import NUMLIGHFD"
    code = "NUMLIGHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMLIGHFD'):
            return

        self.merge_existing(models.Ligplaats, r['NUMLIGHFD/LIG/sleutelVerzendend'], dict(
            hoofdadres_id=self.foreign_key_id(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportStaTask(batch.AbstractUvaTask):
    name = "import STA"
    code = "STA"

    def execute(self):
        models.Standplaats.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'STABRN', 'STASTS', 'STABRT'):
            return

        self.create(models.Standplaats(
            pk=r['sleutelverzendend'],
            identificatie=r['Standplaatsidentificatie'],
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            document_nummer=r['DocumentnummerMutatieStandplaats'],
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieStandplaats']),
            bron_id=self.foreign_key_id(models.Bron, r['STABRN/BRN/Code']),
            status_id=self.foreign_key_id(models.Status, r['STASTS/STS/Code']),
            buurt_id=self.foreign_key_id(models.Buurt, r['STABRT/BRT/sleutelVerzendend'])
        ))


class ImportNumStaHfdTask(batch.AbstractUvaTask):
    name = "import NUMSTAHFD"
    code = "NUMSTAHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMSTAHFD'):
            return

        self.merge_existing(models.Standplaats, r['NUMSTAHFD/STA/sleutelVerzendend'], dict(
            hoofdadres_id=self.foreign_key_id(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportVboTask(batch.AbstractUvaTask):
    name = "import VBO"
    code = "VBO"

    def execute(self):
        models.Verblijfsobject.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'VBOAVR', 'VBOBRN', 'VBOEGM', 'VBOFNG', 'VBOGBK', 'VBOLOC', 'VBOLGG', 'VBOMNT',
                                     'VBOTGG', 'VBOOVR', 'VBOSTS', 'VBOBRT'):
            return

        x = r['X-Coordinaat']
        y = r['Y-Coordinaat']
        if x and y:
            geo = Point(int(x), int(y))
        else:
            geo = None

        self.create(models.Verblijfsobject(
            pk=r['sleutelverzendend'],
            identificatie=(r['Verblijfsobjectidentificatie']),
            geometrie=geo,
            gebruiksdoel_code=(r['GebruiksdoelVerblijfsobjectDomein']),
            gebruiksdoel_omschrijving=(r['OmschrijvingGebruiksdoelVerblijfsobjectDomein']),
            oppervlakte=uva2.uva_nummer(r['OppervlakteVerblijfsobject']),
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatieVerblijfsobject']),
            document_nummer=(r['DocumentnummerMutatieVerblijfsobject']),
            bouwlaag_toegang=uva2.uva_nummer(r['Bouwlaagtoegang']),
            status_coordinaat_code=(r['StatusCoordinaatDomein']),
            status_coordinaat_omschrijving=(r['OmschrijvingCoordinaatDomein']),
            bouwlagen=uva2.uva_nummer(r['AantalBouwlagen']),
            type_woonobject_code=(r['TypeWoonobjectDomein']),
            type_woonobject_omschrijving=(r['OmschrijvingTypeWoonobjectDomein']),
            woningvoorraad=uva2.uva_indicatie(r['IndicatieWoningvoorraad']),
            aantal_kamers=uva2.uva_nummer(r['AantalKamers']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            reden_afvoer_id=self.foreign_key_id(models.RedenAfvoer, r['VBOAVR/AVR/Code']),
            bron_id=self.foreign_key_id(models.Bron, r['VBOBRN/BRN/Code']),
            eigendomsverhouding_id=self.foreign_key_id(models.Eigendomsverhouding, r['VBOEGM/EGM/Code']),
            financieringswijze_id=self.foreign_key_id(models.Financieringswijze, r['VBOFNG/FNG/Code']),
            gebruik_id=self.foreign_key_id(models.Gebruik, r['VBOGBK/GBK/Code']),
            locatie_ingang_id=self.foreign_key_id(models.LocatieIngang, r['VBOLOC/LOC/Code']),
            ligging_id=self.foreign_key_id(models.Ligging, r['VBOLGG/LGG/Code']),
            # ?=(r['VBOMNT/MNT/Code']),
            toegang_id=self.foreign_key_id(models.Toegang, r['VBOTGG/TGG/Code']),
            # ?=(r['VBOOVR/OVR/Code']),
            status_id=self.foreign_key_id(models.Status, r['VBOSTS/STS/Code']),
            buurt_id=self.foreign_key_id(models.Buurt, r['VBOBRT/BRT/sleutelVerzendend']),
        ))


class ImportNumVboHfdTask(batch.AbstractUvaTask):
    name = "import NUMVBOHFD"
    code = "NUMVBOHFD"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'NUMVBOHFD'):
            return

        self.merge_existing(models.Verblijfsobject, r['NUMVBOHFD/VBO/sleutelVerzendend'], dict(
            hoofdadres_id=self.foreign_key_id(models.Nummeraanduiding, r['IdentificatiecodeNummeraanduiding'])
        ))


class ImportPndTask(batch.AbstractUvaTask):
    name = "import PND"
    code = "PND"

    def execute(self):
        models.Pand.objects.all().delete()
        super().execute()

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDSTS', 'PNDBBK'):
            return

        self.create(models.Pand(
            pk=r['sleutelverzendend'],
            identificatie=(r['Pandidentificatie']),
            document_mutatie=uva2.uva_datum(r['DocumentdatumMutatiePand']),
            document_nummer=(r['DocumentnummerMutatiePand']),
            bouwjaar=uva2.uva_nummer(r['OorspronkelijkBouwjaarPand']),
            laagste_bouwlaag=uva2.uva_nummer(r['LaagsteBouwlaag']),
            hoogste_bouwlaag=uva2.uva_nummer(r['HoogsteBouwlaag']),
            pandnummer=(r['Pandnummer']),
            vervallen=uva2.uva_indicatie(r['Indicatie-vervallen']),
            status_id=self.foreign_key_id(models.Status, r['PNDSTS/STS/Code']),
        ))


class ImportPndVboTask(batch.AbstractUvaTask):
    name = "import PNDVBO"
    code = "PNDVBO"

    def process_row(self, r):
        if not uva2.geldig_tijdvak(r):
            return

        if not uva2.geldige_relaties(r, 'PNDVBO'):
            return

        pand_id = r['sleutelverzendend']
        vbo_id = r['PNDVBO/VBO/sleutelVerzendend']

        try:
            vbo = models.Verblijfsobject.objects.get(pk=vbo_id)
            vbo.panden.add(models.Pand.objects.get(pk=pand_id))
        except models.Verblijfsobject.DoesNotExist:
            log.warn("Non-existing verblijfsobject: %s", vbo_id)


class ImportStaGeoTask(batch.AbstractWktTask):
    name = "import STA WKT"
    source_file = "BAG_STANDPLAATS_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        self.merge_existing(models.Standplaats, '0' + row_id, dict(
            geometrie=geom,
        ))


class ImportLigGeoTask(batch.AbstractWktTask):
    name = "import LIG WKT"
    source_file = "BAG_LIGPLAATS_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        self.merge_existing(models.Ligplaats, '0' + row_id, dict(
            geometrie=geom
        ))


class ImportPndGeoTask(batch.AbstractWktTask):
    name = "import PND WKT"
    source_file = "BAG_PAND_GEOMETRIE.dat"

    def process_row(self, row_id, geom):
        self.merge_existing(models.Pand, '0' + row_id, dict(
            geometrie=geom
        ))
