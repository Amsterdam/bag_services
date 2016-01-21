# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0001_squashed_0042_auto_20151210_0952'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP VIEW IF EXISTS geo_bag_gebiedsgerichtwerken
            """
        ),
        migrations.RunSQL(
            sql="""
            DROP VIEW IF EXISTS geo_bag_grootstedelijkgebied
            """
        ),
        migrations.RunSQL(
            sql="""
            DROP VIEW IF EXISTS geo_bag_unesco
            """
        ),
        migrations.AlterField(
            model_name='gebiedsgerichtwerken',
            name='id',
            field=models.CharField(primary_key=True, serialize=False, max_length=4),
        ),
        migrations.AlterField(
            model_name='grootstedelijkgebied',
            name='id',
            field=models.SlugField(primary_key=True, serialize=False, max_length=100),
        ),
        migrations.AlterField(
            model_name='unesco',
            name='id',
            field=models.SlugField(primary_key=True, serialize=False, max_length=100),
        ),
        migrations.RunSQL(
                sql="""
CREATE VIEW geo_bag_gebiedsgerichtwerken AS
SELECT
  g.id                                                           AS id,
  g.code                                                         AS code,
  g.naam                                                         AS naam,
  g.geometrie                                                    AS geometrie,
  g.naam                                                         AS display,
  'gebieden/gebiedsgerichtwerken'                                AS type,
  site.domain || 'gebieden/gebiedsgerichtwerken/' || g.id || '/' AS uri
FROM bag_gebiedsgerichtwerken g, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrations.RunSQL(
            sql="""
CREATE VIEW geo_bag_grootstedelijkgebied AS
SELECT
  gg.id                                                           AS id,
  gg.naam                                                         AS naam,
  gg.geometrie                                                    AS geometrie,
  gg.naam                                                         AS display,
  'gebieden/grootstedelijkgebied'                                 AS type,
  site.domain || 'gebieden/grootstedelijkgebied/' || gg.id || '/' AS uri
FROM bag_grootstedelijkgebied gg, django_site site
WHERE site.name = 'API Domain'
            """
        ),
        migrations.RunSQL(
                sql="""
CREATE VIEW geo_bag_unesco AS
SELECT
  u.id                                             AS id,
  u.naam                                           AS naam,
  u.geometrie                                      AS geometrie,
  u.naam                                           AS display,
  'gebieden/unesco'                                AS type,
  site.domain || 'gebieden/unesco/' || u.id || '/' AS uri
FROM bag_unesco u, django_site site
WHERE site.name = 'API Domain'
""",
        ),

    ]
