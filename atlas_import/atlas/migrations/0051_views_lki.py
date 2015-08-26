# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0050_replace_beperking_lkikadastraalobject_view2'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
DROP VIEW IF EXISTS atlas_geo_lki_gemeente;
DROP VIEW IF EXISTS atlas_geo_lki_kadastralegemeente;
DROP VIEW IF EXISTS atlas_geo_lki_sectie;
DROP VIEW IF EXISTS atlas_geo_lki_kadastraalobject;

CREATE OR REPLACE VIEW atlas_geo_lki_gemeente AS 
  SELECT 
    id,
    gemeentenaam,
    geometrie
  FROM atlas_lkigemeente;

CREATE OR REPLACE VIEW atlas_geo_lki_kadastralegemeente AS 
  SELECT 
    id,
    code,
    geometrie
  FROM atlas_lkikadastralegemeente;

CREATE OR REPLACE VIEW atlas_geo_lki_sectie AS 
  SELECT 
    id,
    code,
    geometrie
  FROM atlas_lkisectie;

CREATE OR REPLACE VIEW atlas_geo_lki_kadastraalobject AS 
  SELECT 
    id,
    perceelnummer,
    geometrie
  FROM atlas_lkikadastraalobject;''',
            reverse_sql='''
DROP VIEW atlas_geo_lki_gemeente;
DROP VIEW atlas_geo_lki_kadastralegemeente;
DROP VIEW atlas_geo_lki_sectie;
DROP VIEW atlas_geo_lki_kadastraalobject;''',
        )
    ]
