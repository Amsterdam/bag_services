"""
collect and validate bag, brk, gebieden and wkpb table counts
"""
import logging
from django.db import connection


LOG = logging.getLogger(__name__)

TABLE_TARGETS = [
    # counts from 15-10-2018
    (8597       ,"bag_bouwblok"),
    (100        ,"bag_bron"),
    (481        ,"bag_buurt"),
    (99         ,"bag_buurtcombinatie"),
    (2          ,"bag_eigendomsverhouding"),
    (19         ,"bag_financieringswijze"),
    (22         ,"bag_gebiedsgerichtwerken"),
    (320        ,"bag_gebruik"),
    (515178     ,"bag_gebruiksdoel"),
    (1          ,"bag_gemeente"),
    (36         ,"bag_grootstedelijkgebied"),
    (515370     ,"bag_indicatieadresseerbaarobject"),
    (6          ,"bag_ligging"),
    (2913       ,"bag_ligplaats"),
    (5          ,"bag_locatieingang"),
    (517683     ,"bag_nummeraanduiding"),
    (6191       ,"bag_openbareruimte"),
    (184345     ,"bag_pand"),
    (44         ,"bag_redenafvoer"),
    (44         ,"bag_redenopvoer"),
    (8          ,"bag_stadsdeel"),
    (323        ,"bag_standplaats"),
    (43         ,"bag_status"),
    (9          ,"bag_toegang"),
    (2          ,"bag_unesco"),
    (512154     ,"bag_verblijfsobject"),
    (513315     ,"bag_verblijfsobjectpandrelatie"),
    (1          ,"bag_woonplaats"),
    (4          ,"brk_aanduidingnaam"),
    (386955     ,"brk_aantekening"),
    (31         ,"brk_aardaantekening"),
    (12         ,"brk_aardzakelijkrecht"),
    (225800     ,"brk_adres"),
    (971430     ,"brk_aperceelgperceelrelatie"),
    (6          ,"brk_appartementsrechtssplitstype"),
    (411285     ,"brk_bebouwde_a_percelen"),
    (303286     ,"brk_bebouwde_g_percelen"),
    (8          ,"brk_beschikkingsbevoegdheid"),
    (65         ,"brk_cultuurcodebebouwd"),
    (23         ,"brk_cultuurcodeonbebouwd"),
    (342886     ,"brk_eigenaar"),
    (10          ,"brk_eigenaarcategorie"),
    (921398     ,"brk_eigendom"),
    (143945     ,"brk_erfpacht"),
    (19         ,"brk_gemeente"),
    (3          ,"brk_geslacht"),
    (587902     ,"brk_kadastraalobject"),
    (521751     ,"brk_kadastraalobjectverblijfsobjectrelatie"),
    (342886     ,"brk_kadastraalsubject"),
    (65         ,"brk_kadastralegemeente"),
    (170        ,"brk_kadastralesectie"),
    (383518     ,"brk_kot_orig_diva_location"),
    (253        ,"brk_land"),
    (20         ,"brk_rechtsvorm"),
    (2          ,"brk_soortgrootte"),
    (921260     ,"brk_zakelijkrecht"),
    (872015     ,"brk_zakelijkrechtverblijfsobjectrelatie"),
    (57         ,"django_content_type"),
    (19         ,"django_migrations"),
    (5757       ,"spatial_ref_sys"),
    (5184       ,"wkpb_beperking"),
    (20         ,"wkpb_beperkingcode"),
    (314047     ,"wkpb_beperkingkadastraalobject"),
    (338702     ,"wkpb_beperkingverblijfsobject"),
    (6          ,"wkpb_broncode"),
    (7354       ,"wkpb_brondocument"),
]


def sql_count(table):

    count = 0

    with connection.cursor() as c:
        c.execute('SELECT COUNT(*) FROM {}'.format(connection.ops.quote_name(table)))
        row = c.fetchone()
        count += row[0]
        # LOG.debug('COUNT %-6s %s', count, table)

    return count


def check_table_counts(table_data: list):
    """
    Given list with tuples of count - table name
    check if current table counts are close
    """
    error = False
    all_msg = ("Table count errors \n"
               "Count ,   Target,  Deviation-Allowed,      Table,           Status \n")

    for target, table in table_data:
        count = sql_count(table)
        delta = abs(count - target)
        deviation = int(0.05 * target)
        if delta > deviation or count == 0:
            status = '<FAIL>'
            error = True
        else:
            status = '< OK >'

        msg = f"{count:>6} ~= {target:<11} {delta:>6}-{deviation:<6} {table:<42} {status} \n"
        all_msg += msg

    if error:
        LOG.error(msg)
        raise ValueError(all_msg)
    else:
        LOG.debug(all_msg)


def check_table_targets():
    """
    Check if tables have a specific count
    """
    LOG.debug('Validating table counts..')

    # Count,   table
    check_table_counts(TABLE_TARGETS)
