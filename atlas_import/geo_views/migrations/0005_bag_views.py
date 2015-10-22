# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    """
    bij buurt, buurtcombinatie, stadsdeel en gebiedsgericht werken: naam en (volledige) code.
    Bij grootstedelijk project en unesco: naam.
    Bij bouwblok: code
    """
    dependencies = [
        ('geo_views', '0004_lki_views'),
        ('bag', '0010_buurtcombinatie_gebiedsgerichtwerken_grootstedelijkproject_unesco')
    ]

    operations = [
        migrate.ManageView(view_name="geo_bag_stadsdeel",
                           sql="SELECT id, code, naam, geometrie FROM bag_stadsdeel"),
        migrate.ManageView(view_name="geo_bag_buurt",
                           sql="SELECT id, code, naam, geometrie FROM bag_buurt"),
        migrate.ManageView(view_name="geo_bag_bouwblok",
                           sql="SELECT id, code, geometrie FROM bag_bouwblok"),
        migrate.ManageView(view_name="geo_bag_buurtcombinatie",
                           sql="SELECT id, vollcode, naam, geometrie FROM bag_buurtcombinatie"),
        migrate.ManageView(view_name="geo_bag_gebiedsgerichtwerken",
                           sql="SELECT id, code, naam, geometrie FROM bag_gebiedsgerichtwerken"),
        migrate.ManageView(view_name="geo_bag_grootstedelijkgebied",
                           sql="SELECT id, naam, geometrie FROM bag_grootstedelijkgebied"),
        migrate.ManageView(view_name="geo_bag_unesco",
                           sql="SELECT id, naam, geometrie FROM bag_unesco"),
    ]
