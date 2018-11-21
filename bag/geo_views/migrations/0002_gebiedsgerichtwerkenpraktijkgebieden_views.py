
# -*- coding: utf-8 -*-

from django.db import migrations

from geo_views import migrate

from django.conf import settings

from psycopg2.extensions import QuotedString

URL = settings.DATAPUNT_API_URL


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0001_squashed_0010_brk_wkpb_views')
    ]

    operations = [
        migrate.ManageView(
            view_name='geo_bag_gebiedsgerichtwerkenpraktijkgebieden',
            sql="""
SELECT
  g.id                                                           AS id,
  g.naam                                                         AS naam,
  g.geometrie                                                    AS geometrie,
  g.naam                                                         AS display,
  'gebieden/gebiedsgerichtwerkenpraktijkgebieden'::TEXT         AS type,
  {} || 'gebieden/gebiedsgerichtwerkenpraktijkgebieden/' || g.id || '/' AS uri
FROM bag_gebiedsgerichtwerkenpraktijkgebieden g
""".format(QuotedString(URL))
        )
    ]
