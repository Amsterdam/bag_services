# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('bag', '0003_auto_20150908_1255')
    ]

    operations = [
        migrate.ManageView(view_name="geo_bag_ligplaats", sql="SELECT id, geometrie FROM bag_ligplaats"),
        migrate.ManageView(view_name="geo_bag_standplaats", sql="SELECT id, geometrie FROM bag_standplaats"),
        migrate.ManageView(view_name="geo_bag_verblijfsobject", sql="SELECT id, geometrie FROM bag_verblijfsobject"),
        migrate.ManageView(view_name="geo_bag_pand", sql="SELECT id, geometrie FROM bag_pand"),
    ]
