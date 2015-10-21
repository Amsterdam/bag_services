# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0004_lki_views'),
        ('bag', '0009_auto_20151020_1804')
    ]

    operations = [
        migrate.ManageView(view_name="geo_bag_stadsdeel", sql="SELECT id, geometrie FROM bag_stadsdeel"),
        migrate.ManageView(view_name="geo_bag_buurt", sql="SELECT id, geometrie FROM bag_buurt"),
        migrate.ManageView(view_name="geo_bag_bouwblok", sql="SELECT id, geometrie FROM bag_bouwblok"),
    ]
