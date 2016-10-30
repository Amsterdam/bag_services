# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations  # models

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0001_squashed_0010_brk_wkpb_views'),
    ]

    operations = [

        migrate.ManageView(
            view_name='geo_bag_openbareruimte',
            sql="""
SELECT
  opr.id                                                AS id,
  opr.naam                                              AS display,
  CASE opr.type
    WHEN '01' THEN 'Weg'
        WHEN '02' THEN 'Water'
        WHEN '03' THEN 'Spoorbaan'
        WHEN '04' THEN 'Terrein'
        WHEN '05' THEN 'Kunstwerk'
        WHEN '06' THEN 'Landschappelijk gebied'
        WHEN '07' THEN 'Administratief gebied'
        ELSE '??'
  END                                                   AS opr_type,
  opr.geometrie                                         AS geometrie,
  'bag/openbareruimte'                                  AS type,
  site.domain || 'bag/openbareruimte/' || opr.id || '/' AS uri
FROM
  bag_openbareruimte opr
  ,
  django_site site
WHERE
  site.name = 'API Domain'
                """,

        )

    ]
