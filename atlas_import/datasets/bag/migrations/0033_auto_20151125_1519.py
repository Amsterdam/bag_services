# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


DROP_VIEW = """
DROP VIEW IF EXISTS geo_bag_buurtcombinatie;
"""

CREATE_VIEW = """
CREATE VIEW geo_bag_buurtcombinatie AS
SELECT
  bc.id                                                      AS id,
  bc.vollcode                                                AS vollcode,
  bc.naam                                                    AS naam,
  bc.geometrie                                               AS geometrie,
  bc.naam                                                    AS display,
  'gebieden/buurtcombinatie'                                 AS type,
  site.domain || 'gebieden/buurtcombinatie/' || bc.id || '/' AS uri
FROM bag_buurtcombinatie bc, django_site site
WHERE site.name = 'API Domain'
;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0032_auto_20151125_1449'),
    ]

    operations = [
        migrations.RunSQL(sql=DROP_VIEW, reverse_sql=CREATE_VIEW),
        migrations.AlterField(
            model_name='buurtcombinatie',
            name='id',
            field=models.CharField(primary_key=True, serialize=False, max_length=14),
        ),
        migrations.RunSQL(sql=CREATE_VIEW, reverse_sql=DROP_VIEW),
    ]
