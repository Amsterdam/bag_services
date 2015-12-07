# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0008_wkpb_view'),
        ('bag', '0037_openbareruimte_geometrie'),
    ]

    operations = [
        migrate.ManageView(view_name='geo_bag_openbareruimte', sql="""
SELECT
  opr.id                                                AS id,
  opr.naam                                              AS display,
  opr.type                                              AS opr_type,
  opr.geometrie                                         AS geometrie,
  'bag/openbareruimte'                                  AS type,
  site.domain || 'bag/openbareruimte/' || opr.id || '/' AS uri
FROM
  bag_openbareruimte opr
  ,
  django_site site
WHERE
  site.name = 'API Domain'
            """)
    ]
