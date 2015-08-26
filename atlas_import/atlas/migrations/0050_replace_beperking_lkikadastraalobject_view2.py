# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0049_auto_20150826_1044'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
DROP VIEW IF EXISTS atlas_geo_wkpb;

CREATE OR REPLACE VIEW atlas_geo_wkpb AS 
  SELECT 
    bk.id as id,
    bp.id as beperking_id,
    bp.beperkingtype_id,
    ko.id as kadastraal_object_id,
    ko.geometrie as geometrie
  FROM
    atlas_beperking bp,
    atlas_beperkingkadastraalobject bk,
    atlas_lkikadastraalobject ko
  WHERE 
    bp.id = bk.beperking_id 
    AND 
    ko.id = bk.kadastraal_object_id;''',
            reverse_sql='DROP VIEW IF EXISTS atlas_geo_wkpb',
        )
    ]
