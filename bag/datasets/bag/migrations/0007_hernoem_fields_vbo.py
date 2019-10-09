import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0006_auto_20191008_1132'),
    ]

    operations = [
        migrations.RenameField(
            model_name='verblijfsobject',
            old_name='verhuurbare_eenheden',
            new_name='aantal_eenheden_complex',
        ),
        migrations.RenameField(
            model_name='verblijfsobject',
            old_name='toegangen',
            new_name='toegang',
        ),
        migrations.RenameField(
            model_name='verblijfsobject',
            old_name='gebruiksdoelen',
            new_name='gebruiksdoel',
        ),
    ]
