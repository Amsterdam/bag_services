# Generated by Django 2.2.28 on 2022-06-09 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0005_auto_20210707_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastraalsubject',
            name='bsn',
            field=models.CharField(null=True, max_length=9),
        ),
    ]
