# Generated by Django 2.2.28 on 2023-07-20 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0006_kadastraalsubject_bsn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='statutaire_zetel',
            field=models.CharField(max_length=60, null=True),
        ),
    ]