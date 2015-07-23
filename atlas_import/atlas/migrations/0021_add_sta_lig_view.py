# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0020_verblijfsobject_panden'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
CREATE VIEW atlas_geo_ligplaats AS
SELECT
  l.id,
  l.geometrie,
  n.huisnummer,
  n.huisnummer_toevoeging,
  n.huisletter
FROM atlas_ligplaats l LEFT JOIN atlas_nummeraanduiding n ON l.hoofdadres_id = n.id''',
            reverse_sql='DROP VIEW atlas_geo_ligplaats',
        ),
        migrations.RunSQL(
            sql='''
CREATE VIEW atlas_geo_standplaats AS
SELECT
  s.id,
  s.geometrie,
  n.huisnummer,
  n.huisnummer_toevoeging,
  n.huisletter
FROM atlas_standplaats s LEFT JOIN atlas_nummeraanduiding n ON s.hoofdadres_id = n.id''',
            reverse_sql='DROP VIEW atlas_geo_standplaats',
        )
    ]
