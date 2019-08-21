from batch import batch
from datasets.generic import database
from . import models


class CodeOmschrijvingDataTask(batch.BasicTask):
    model = None
    data = []

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        check_duplicates = set()
        for entry in self.data:
            if entry[1] in check_duplicates:
                raise ValueError(f"Duplicate omschrijving {entry[1]} in {type(self).__name__}")
            check_duplicates.add(entry[1])

        avrs = [self.process_row(entry) for entry in self.data]
        self.model.objects.bulk_create(avrs, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        # noinspection PyCallingNonCallable
        return self.model(pk=r[0], omschrijving=r[1])


data_reden_opvoer_afvoer = [
    ("20", "Geconstateerd VBO"),
    ("10", "Verbouw door wijziging gebruiksdoel"),
    ("11", "Mutatie"),
    ("13", "In onderzoek"),
    ("48", "Niet-gerealiseerd verblijfsobject"),
    ("61", "Nieuwe cyclus"),
    ("12", "Buitengebruik"),
    ("28", "Nieuwbouw vergunningsfase"),
    ("29", "Nieuwbouw in aanbouw"),
    ("60", "Afgevoerde nieuwbouw in aanbouw"),
    ("49", "Correctie afvoer"),
    ("97", "Herstel Reden Opvoer-Afvoer"),
    ("21", "Correctie opvoer"),
    ("30", "Verbouw met nieuwbouwfinanciering"),
    ("31", "Ontstaan door nieuwbouw"),
    ("32", "Ontstaan door samenvoeging"),
    ("33", "Ontstaan door splitsing"),
    ("34", "Verbouw niet-woonobject>woonobject"),
    ("35", "Correctie (+woningvoorraad)"),
    ("36", "Ontstaan door verbouw"),
    ("37", "Verbouw geen invloed woningvoorraad"),
    ("40", "Verdwenen door verbouw"),
    ("41", "Buitengebruik i.v.m. verbouw"),
    ("42", "Verbouw woonobject>niet-woonobject"),
    ("43", "Verdwenen door samenvoeging"),
    ("44", "Verdwenen door splitsing"),
    ("45", "Afgevoerd wegens correctie"),
    ("50", "Gesloopt"),
    ("51", "Buitengebruik i.v.m. brand"),
    ("52", "-"),
    ("99", "Default voor conversie"),
    ("53", "Afgevoerd verbouw geen invloed"),
    ("54", "Afgevoerd administratieve reden"),
    ("46", "Verdwenen door woningonttrekking"),
    ("39", "Administratieve wijziging"),
    ("98", "Dummy Verblijfsobject"),
    ("55", "Afgevoerd bestemmingswijziging"),
    ("63", "Verbouw zolder in woning"),
    ("100", "Vervallen"),
    ("26", "Samenvoeging in vergunningsfase"),
    ("27", "Verbouw in vergunningsfase"),
    ("25", "Splitsing in vergunningsfase"),
    ("24", "Sloop in Vergunningsfase"),
]


class ImportRedenAfvoerTask(CodeOmschrijvingDataTask):
    name = "Import RedenAfvoer"
    model = models.RedenAfvoer
    data = data_reden_opvoer_afvoer


class ImportRedenOpvoerTask(CodeOmschrijvingDataTask):
    name = "Import RedenOpvoer"
    model = models.RedenOpvoer
    data = data_reden_opvoer_afvoer


class ImportStatusTask(CodeOmschrijvingDataTask):
    name = "Import Status"
    model = models.Status
    data = [
        ("08", "Buiten gebruik i.v.m. verbouw"),
        ("09", "Bouwvergunning verleend"),
        ("11", "In Onderzoek (samenvoeging)"),
        ("0", "Actueel"),
        ("2", "Vervallen 1"),
        ("3", "Vervallen 2"),
        ("4", "Vervallen 3"),
        ("5", "Vervallen 4"),
        ("6", "Geconstateerd"),
        ("7", "In Onderzoek"),
        ("01", "Buitengebruik i.v.m. renovatie"),
        ("TMP", "Tijdelijk punt"),
        ("DEF", "Definitief punt"),
        ("10", "In onderzoek (bestemmingswijziging)"),
        ("15", "In onderzoek n.a.v. langdurige leegstand (adressenproject stadsdelen)"),
        ("1", "Vervallen 5"),
        ("13", "In onderzoek n.a.v. langdurige leegstand (adressenproject Dienst Wonen)"),
        ("14", "In onderzoek (adressen project)"),
        ("ONB", "ONB"),
        ("12", "In onderzoek (splitsing)"),
        ("16", "Naamgeving uitgegeven"),
        ("17", "Naamgeving ingetrokken"),
        ("18", "Verblijfsobject gevormd"),
        ("19", "Niet gerealiseerd verblijfsobject"),
        ("20", "Verblijfsobject in gebruik (niet ingemeten)"),
        ("21", "Verblijfsobject in gebruik"),
        ("22", "Verblijfsobject ingetrokken"),
        ("23", "Verblijfsobject buiten gebruik"),
        ("24", "Bouwaanvraag ontvangen"),
        ("26", "Bouw gestart"),
        ("27", "Sloopvergunning verleend"),
        ("28", "Pand gesloopt"),
        ("29", "Niet gerealiseerd pand"),
        ("30", "Pand in gebruik (niet ingemeten)"),
        ("31", "Pand in gebruik"),
        ("32", "Pand buiten gebruik"),
        ("33", "Plaats aangewezen"),
        ("34", "Plaats ingetrokken"),
    ]


class ImportEigendomsverhoudingTask(CodeOmschrijvingDataTask):
    name = "Import Eigendomsverhouding"
    model = models.Eigendomsverhouding
    data = [
        ("01", "Huur"),
        ("02", "Eigendom"),
    ]


class ImportGebruikTask(CodeOmschrijvingDataTask):
    name = "Import Gebruik"
    model = models.Gebruik
    data = [
        ("0001", "ZZ-WONING"),
        ("0002", "ZZ-BEJAARDENWONING"),
        ("0003", "ZZ-WONING VOOR ALLEENSTAANDE"),
        ("0004", "ZZ-INVALIDE-WONING"),
        ("0005", "ZZ-SENIOR-WONING"),
        ("0006", "ZZ-BEDRIJF EN WONING"),
        ("0007", "ZZ-WONING EN ATELIERRUIMTE"),
        ("0008", "ZZ-WONING 2-PERSOONS HUISHOUDEN"),
        ("0009", "ZZ-WONING EN PRAKTIJKRUIMTE"),
        ("0011", "ZZ-EENHEID VOOR STUDENTEN"),
        ("0012", "ZZ-EENHEID VOOR ALLEENSTAANDE"),
        ("0013", "ZZ-EENHEID VOOR BEJAARDE"),
        ("0014", "ZZ-EENHEID VOOR INVALIDE"),
        ("0015", "ZZ-EENHEID IN TEHUIS"),
        ("0030", "ZZ-RECREATIEWONING"),
        ("0040", "ZZ-BIJZONDER WOONGEBOUW"),
        ("0130", "ZZ-WINKEL"),
        ("0131", "ZZ-BANK"),
        ("0132", "ZZ-KANTOOR"),
        ("0133", "ZZ-OVERIGE BEDRIJFSRUIMTE"),
        ("0134", "ZZ-OPSLAG"),
        ("0135", "ZZ-HOTEL"),
        ("0136", "ZZ-HORECA-RUIMTE"),
        ("0137", "ZZ-BOERDERIJ"),
        ("0138", "ZZ-ONDERWIJSINSTELLING"),
        ("0139", "ZZ-GEZONDHEIDSZORG"),
        ("0140", "ZZ-CULTUUR/GEMEENSCHAPSHUIS"),
        ("0141", "ZZ-RECREATIE"),
        ("0142", "ZZ-BENZINESTATION"),
        ("0143", "ZZ-PARKEERGARAGE"),
        ("0144", "ZZ-CREMATORIUM/BEGRAAFPLAATS"),
        ("0145", "ZZ-GEMAAL/WATERZUIVERING"),
        ("0146", "ZZ-GEVANGENIS"),
        ("0147", "ZZ-POLITIEBUREAU"),
        ("0148", "ZZ-BRANDWEERKAZERNE"),
        ("0020", "ZZ-COMPLEX VOOR STUDENTEN"),
        ("0021", "ZZ-COMPLEX MET EENHEDEN"),
        ("0041", "ZZ-BEJAARDENTEHUIS"),
        ("0150", "ZZ-BEDRIJF (GEEN WINKEL OF KANTOOR)"),
        ("0151", "ZZ-ATELIERRUIMTE"),
        ("0152", "ZZ-PROSTITUTIE"),
        ("9999", "ZZ-DEFAULT VOOR CONVERSIE"),
        ("0025", "ZZ-JURIDISCH NWOON, BOUWK. WONING"),
        ("0200", "BEST-ligplaats"),
        ("0201", "BEST-standplaats"),
        ("0149", "ZZ-SPORTACCOMODATIE"),
        ("0199", "ZZ-bewoonde andere ruimte"),
        ("0198", "ZZ-GEM. ZOLDER"),
        ("0016", "ZZ-EENHEID OVERIG"),
        ("0029", "ZZ-DIENSTWONING"),
        ("0022", "ZZ-COMPLEX VOOR ALLEENSTAANDEN"),
        ("0023", "ZZ-COMPLEX VOOR BEJAARDEN"),
        ("0024", "ZZ-COMPLEX OVERIG"),
        ("0153", "ZZ-SEXINRICHTING"),
        ("0154", "ZZ-GARAGEBEDRIJF"),
        ("0155", "ZZ-WOONVERBLIJFSINRICHTING"),
        ("0156", "ZZ-RELIGIEUS GEBOUW"),
        ("0157", "ZZ-OPVANGCENTR VOOR VOLWASSENEN"),
        ("0158", "ZZ-WOONVORM RELIGIEUZE GEMSCHAP"),
        ("0159", "ZZ-OPLEIDINGSINTERNAAT"),
        ("0160", "ZZ-OPLINTERN POLITIE/KRYGSMACHT"),
        ("0161", "ZZ-PSYCHIATRISCHE INRICHTING"),
        ("0162", "ZZ-ZWAKZINNIGENINRICHTING"),
        ("0163", "ZZ-VERPLEEGHUIS"),
        ("0164", "ZZ-WOONVORM ZINT/LICH GEHANDIC."),
        ("0165", "ZZ-GEZINSVERVANGEND TEHUIS"),
        ("0166", "ZZ-JEUGDINTERNAAT"),
        ("0167", "ZZ-GARAGEBOX"),
        ("1700", "garage"),
        ("1800", "woning"),
        ("1999", "niet bekend"),
        ("2110", "woning + (detail)handel / winkel"),
        ("2111", "woning + winkel"),
        ("2112", "woning + groothandel"),
        ("2113", "woning + toonzaal"),
        ("2114", "woning + kiosk"),
        ("2119", "woning + (detail)handel overig"),
        ("2120", "woning + horeca"),
        ("2121", "woning + cafetaria/snackbar"),
        ("2122", "woning + café/bar/restaurant"),
        ("2123", "woning + bar/dancing"),
        ("2124", "woning + hotel/motel"),
        ("2125", "woning + pension/logiesgebouw"),
        ("2129", "woning + horeca (overig)"),
        ("2140", "woning + kantoor (hoofdcode)"),
        ("2141", "woning + kantoor"),
        ("2142", "woning + kantoor in bedrijfsverzamelgebouw"),
        ("2144", "woning + studiogebouw"),
        ("2149", "woning + kantoor (overig)"),
        ("2160", "woning + laboratoria / praktijkruimte"),
        ("2161", "woning + laboratorium"),
        ("2162", "woning + praktijkruimte"),
        ("2169", "woning + laboratoria en praktijkruimte (overi"),
        ("2170", "woning + bedrijf"),
        ("2171", "woning + showroom/ werkplaats/ garage"),
        ("2174", "woning + productie (fabriek)"),
        ("2175", "woning + opslag/ distributie"),
        ("2179", "woning + bedrijf (overig)"),
        ("2210", "woning + agrarisch object"),
        ("2211", "woning + akkerbouwbedrijf"),
        ("2212", "woning + tuinbouwbedrijf (incl bloembollentee"),
        ("2213", "woning + fruitkwekerij"),
        ("2214", "woning + champignonteeltbedrijf"),
        ("2215", "woning + witlofteeltbedrijf"),
        ("2216", "woning + boomkwekerijbedrijf  (incl sierteelt"),
        ("2217", "woning + bosbouwbedrijf"),
        ("2218", "woning + tuincentrum"),
        ("2241", "woning + proefboerderij  (zowel akkerbouw als"),
        ("2242", "woning + gemengd bedrijf (zowel akkerbouw als"),
        ("2243", "woning + melkveebedrijf"),
        ("2244", "woning + kaasboerderij"),
        ("2245", "woning + intensieve veehouderij runderen"),
        ("2246", "woning + intensieve veehouderij varkens"),
        ("2247", "woning + KI-station"),
        ("2248", "woning + intensieve veehouderij pluimvee"),
        ("2261", "woning + stoeterij / manege / paardenfokkerij"),
        ("2262", "woning + viskwekerij"),
        ("2264", "woning + loonwerkbedrijf"),
        ("2265", "woning + pelsdierfokkerij"),
        ("2266", "woning + broederij"),
        ("2299", "woning + agrarische niet-woning (overig)"),
        ("2450", "woning + eredienst"),
        ("2451", "woning + kerk"),
        ("2452", "woning + kapel"),
        ("2453", "woning + moskee"),
        ("2459", "woning + eredienst (overig)"),
        ("2525", "woning + camping"),
        ("3110", "(detail)handel / winkel"),
        ("3111", "winkel"),
        ("3112", "groothandel"),
        ("3113", "toonzaal"),
        ("3114", "kiosk"),
        ("3119", "overig (detail)handel"),
        ("3120", "horeca"),
        ("3121", "cafetaria / snackbar"),
        ("3122", "café / bar / restaurant"),
        ("3123", "bar / dancing"),
        ("3124", "hotel / motel"),
        ("3125", "pension / logiesgebouw"),
        ("3129", "overig horeca"),
        ("3140", "kantoor (hoofdcode)"),
        ("3141", "kantoor"),
        ("3142", "kantoor in bedrijfsverzamelgebouw"),
        ("3144", "studiogebouw"),
        ("3149", "overig kantoor"),
        ("3160", "laboratorium / praktijkruimte"),
        ("3161", "laboratorium"),
        ("3162", "praktijkruimte"),
        ("3169", "overig laboratorium en praktijkruimte"),
        ("3170", "bedrijf"),
        ("3171", "showroom / werkplaats / garage"),
        ("3174", "productie (fabriek)"),
        ("3175", "opslag / distributie"),
        ("3179", "overig bedrijf"),
        ("3210", "agrarisch object"),
        ("3211", "akkerbouwbedrijf"),
        ("3212", "tuinbouwbedrijf (incl bloembollenteelt)"),
        ("3213", "fruitkwekerij"),
        ("3214", "champignonteeltbedrijf"),
        ("3215", "witlofteeltbedrijf"),
        ("3216", "boomkwekerijbedrijf (inclusief sierteeltbedri"),
        ("3217", "bosbouwbedrijf"),
        ("3218", "tuincentrum"),
        ("3241", "proefboerderij (zowel akkerbouw als veeteelt)"),
        ("3242", "gemengd bedrijf (zowel akkerbouw als vee)"),
        ("3243", "melkveebedrijf"),
        ("3244", "kaasboerderij"),
        ("3245", "intensieve veehouderij runderen"),
        ("3246", "intensieve veehouderij varkens"),
        ("3247", "KI-station"),
        ("3248", "intensieve veehouderij pluimvee"),
        ("3261", "stoeterij / manege / paardenfokkerij"),
        ("3262", "viskwekerij"),
        ("3263", "kinderboerderij"),
        ("3264", "loonwerkbedrijf"),
        ("3265", "pelsdierfokkerij"),
        ("3266", "broederij"),
        ("3299", "overige agrarische niet-woningen"),
        ("3310", "onderwijs"),
        ("3311", "crèche / peuterspeelzaal"),
        ("3312", "basisschool"),
        ("3313", "algemeen voortgezet onderwijs  (MAVO / HAVO /"),
        ("3314", "beroepsonderwijs  (LBO / MBO)"),
        ("3315", "hogeschool / universiteit"),
        ("3316", "vrijetijdsonderwijs"),
        ("3317", "speciaal onderwijs"),
        ("3318", "dagverblijf"),
        ("3319", "overig onderwijs"),
        ("3330", "medisch"),
        ("3331", "ziekenhuis"),
        ("3332", "(poli)kliniek"),
        ("3333", "medisch dagverblijf"),
        ("3334", "psychiatrisch ziekenhuis"),
        ("3335", "revalidatiecentrum"),
        ("3336", "verpleegtehuis"),
        ("3337", "gezinsvervangend tehuis"),
        ("3338", "verblijf voor verstandelijk gehandicapten"),
        ("3339", "overig medisch"),
        ("3350", "bijzondere woonfunctie"),
        ("3351", "verzorgings- / bejaardentehuis (complex)"),
        ("3352", "kruisgebouw"),
        ("3353", "praktijkruimte (tandarts / fysiotherapeut)"),
        ("3354", "kindertehuis"),
        ("3355", "sociale werkvoorziening"),
        ("3356", "gevangenis"),
        ("3357", "klooster"),
        ("3358", "kazerne"),
        ("3359", "overige bijzondere woonfuncties"),
        ("3370", "gemeenschapsgebouw"),
        ("3371", "gemeentehuis"),
        ("3372", "gemeentewerken"),
        ("3373", "politiebureau"),
        ("3374", "gerechtsgebouw"),
        ("3375", "brandweerkazerne"),
        ("3376", "wijk- / buurtcentrum"),
        ("3377", "begraafplaats"),
        ("3378", "aula"),
        ("3379", "crematorium"),
        ("3389", "overig gemeenschapsgebouw"),
        ("3410", "cultuur"),
        ("3411", "schouwburg / concertgebouw"),
        ("3412", "congresgebouw"),
        ("3413", "museum"),
        ("3414", "expositiehal / evenementenhal"),
        ("3415", "bioscoop"),
        ("3416", "bibliotheek"),
        ("3417", "kasteel / paleis"),
        ("3419", "overig cultureel"),
        ("3450", "eredienst"),
        ("3451", "kerk"),
        ("3452", "kapel"),
        ("3453", "moskee"),
        ("3459", "overig eredienst"),
        ("3510", "sport / recreatie"),
        ("3511", "sporthal / sportzaal / gymnastieklokaal"),
        ("3512", "sportterrein"),
        ("3513", "stadion"),
        ("3514", "tribune"),
        ("3515", "clubhuis"),
        ("3516", "kleedgebouw / toiletten"),
        ("3517", "kantine"),
        ("3518", "recreatie / sportcentrum"),
        ("3519", "tennisbaan"),
        ("3520", "ijsbaan"),
        ("3521", "zwembad"),
        ("3522", "sauna"),
        ("3529", "overig sport en recreatie"),
        ("3532", "kampeerboerderij"),
        ("3610", "dienstverlening openbaar nut"),
        ("3614", "watertoren"),
        ("3617", "gemaal"),
        ("3618", "gasdistributiestation"),
        ("3619", "stroomdistributiestation"),
        ("3620", "drinkwaterpompstation"),
        ("3621", "trafo"),
        ("3624", "windmolen"),
        ("3629", "overig energie en water"),
        ("3630", "transport"),
        ("3633", "vuurtoren"),
        ("3635", "busstation"),
        ("3638", "benzinestation"),
        ("3639", "overig transport"),
        ("3644", "NS-station (gebouwen)"),
        ("3660", "communicatie"),
        ("3661", "postkantoor / bankgebouw"),
        ("3663", "postsorteerbedrijf"),
        ("3664", "telefooncentrale"),
        ("3669", "overig communicatie"),
        ("3690", "tbv landsverdediging"),
        ("4100", "terrein"),
        ("1000", "BEST-woonfunctie"),
        ("1010", "BEST-woning"),
        ("1011", "BEST-bejaarden/aanleunwoning"),
        ("1012", "BEST-invalidenwoning"),
        ("1020", "BEST-gemengde panden"),
        ("1030", "BEST-wooneenheden"),
        ("1031", "BEST-studenteneenheid"),
        ("1032", "BEST-bejaardeneenheid"),
        ("1033", "BEST-invalideneenheid"),
        ("1040", "BEST-complex met eenheden"),
        ("1041", "BEST-studenteneenheid in complex met 1 adres"),
        ("1042", "BEST-bejaardeneenheid in complex met 1 adres"),
        ("1043", "BEST-invalideneenheid in complex met 1 adres"),
        ("1050", "BEST-bijzondere woongebouwen"),
        ("1051", "BEST-bejaardentehuis"),
        ("1052", "BEST-klooster"),
        ("1053", "BEST-kindertehuis"),
        ("1054", "BEST-internaat"),
        ("1100", "BEST-bijeenkomstfunctie"),
        ("1200", "BEST-celfunctie"),
        ("1300", "BEST-gezondheidszorgfunctie"),
        ("1310", "BEST-verpleeghuis"),
        ("1320", "BEST-inrichting"),
        ("1400", "BEST-industriefunctie"),
        ("1500", "BEST-kantoorfunctie"),
        ("1600", "BEST-logiesfunctie"),
        ("1610", "BEST-recreatiewoningen"),
        ("0600", "BEST-sportfunctie"),
        ("0700", "BEST-onderwijsfunctie"),
        ("0800", "BEST-winkelfunctie"),
        ("0900", "BEST-overige gebruiksfunctie"),
        ("0999", "BEST-onbekend"),
        ("1810", "woonwagen / stacaravan"),
        ("1820", "woonboot"),
        ("3172", "bedrijfsboot"),
        ("1710", "collectieve parkeerplaats bij woningen"),
        ("1750", "parkeerplaats (dienstbaar aan wonen)"),
        ("3525", "camping"),
        ("3612", "reinwaterkelder"),
        ("3613", "drinkwaterzuiveringsinstallatie"),
        ("3634", "NS-station"),
        ("3637", "parkeerplaats (niet dienstbaar aan wonen)"),
        ("3641", "parkeergarage geëxploiteerd voor kortparkeren"),
        ("3668", "geldautomaat / pinautomaat"),
        ("4113", "volkstuin"),
        ("4114", "speeltuin"),
        ("3636", "parkeerplaats in parkeergarage"),
        ("2176", "atelier / werkruimte met woning"),
        ("3176", "atelier / werkruimte"),
        ("3361", "bordeel / relaxruimte"),
        ("2330", "2330 Complex,onzelfst. woonruimten met begeleiding"),
        ("2310", "2310 Verpleeghuis"),
        ("2085", "2085 Complex, onzelfst. woonruimten"),
        ("2083", "2083 Complex, onzelfst. gehandicaptenwoonruimten"),
        ("2082", "2082 Complex, onzelfst. seniorenwoonruimten"),
        ("2081", "2081 Complex, onzelfst. studentenwoonruimten"),
        ("2075", "2075 Woning"),
        ("2070", "2070 Studentenwoning"),
        ("2061", "2061 Rolstoeltoegankelijke woning"),
        ("2060", "2060 Seniorenwoning"),
    ]


class ImportToegangTask(CodeOmschrijvingDataTask):
    name = "Import Toegang"
    model = models.Toegang
    data = [
        ("01", "Trap"),
        ("02", "Galerij + trap"),
        ("03", "Lift"),
        ("04", "Galerij + lift"),
        ("05", "Centrale hal"),
        ("06", "Trap / centrale hal"),
        ("07", "Lift / centrale hal"),
        ("99", "Onbekend"),
        ("08", "Begane grond"),
    ]
