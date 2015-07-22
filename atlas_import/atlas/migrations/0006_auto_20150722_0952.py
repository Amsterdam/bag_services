# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0005_openbareruimte'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nummeraanduiding',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(null=True, max_length=20)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(unique=True, max_length=14)),
                ('huisnummer', models.CharField(max_length=5)),
                ('huisletter', models.CharField(null=True, max_length=1)),
                ('huisnummer_toevoeging', models.CharField(null=True, max_length=4)),
                ('postcode', models.CharField(null=True, max_length=6)),
                ('type', models.CharField(null=True, max_length=2, choices=[('01', 'Verblijfsobject'), ('02', 'Standplaats'), ('03', 'Ligplaats'), ('04', 'Overig gebouwd object'), ('05', 'Overig terrein')])),
                ('adres_nummer', models.CharField(null=True, max_length=10)),
                ('vervallen', models.BooleanField(default=False)),
                ('bron', models.ForeignKey(null=True, to='atlas.Bron')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='type',
            field=models.CharField(null=True, max_length=2, choices=[('01', 'Weg'), ('02', 'Water'), ('03', 'Spoorbaan'), ('04', 'Terrein'), ('05', 'Kunstwerk'), ('06', 'Landschappelijk gebied'), ('07', 'Administratief gebied')]),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='openbare_ruimte',
            field=models.ForeignKey(to='atlas.OpenbareRuimte'),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='status',
            field=models.ForeignKey(null=True, to='atlas.Status'),
        ),
    ]
