# Generated by Django 2.2.10 on 2020-04-07 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0002_add_kadastraobject_ordering_index'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='kadastraalobject',
            name='brk_kot_order_idx',
        ),
        migrations.AlterField(
            model_name='kadastraalobject',
            name='grootte',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddIndex(
            model_name='kadastraalobject',
            index=models.Index(fields=['kadastrale_gemeente', 'sectie', 'perceelnummer', '-indexletter', 'indexnummer'], name='brk_kadastr_kadastr_2c2954_idx'),
        ),
    ]
