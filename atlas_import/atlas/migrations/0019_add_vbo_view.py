# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0018_pand'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
CREATE VIEW atlas_geo_verblijfsobject AS
SELECT
  v.id,
  v.geometrie,
  v.gebruiksdoel_code,
  v.gebruiksdoel_omschrijving,
  n.huisnummer,
  n.huisnummer_toevoeging,
  n.huisletter
FROM atlas_verblijfsobject v LEFT JOIN atlas_nummeraanduiding n ON v.hoofdadres_id = n.id''',
            reverse_sql='DROP VIEW atlas_geo_verblijfsobject',
        )
    ]
