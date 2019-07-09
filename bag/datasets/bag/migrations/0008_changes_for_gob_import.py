# Generated by Django 2.1.10 on 2019-07-04 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0007_grootstedelijkgebied_gsg_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ligplaats',
            name='id',
            field=models.CharField(max_length=16, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='id',
            field=models.CharField(max_length=16, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='id',
            field=models.CharField(max_length=16, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='pand',
            name='id',
            field=models.CharField(max_length=16, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='standplaats',
            name='id',
            field=models.CharField(max_length=16, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='verblijfsobject',
            name='id',
            field=models.CharField(max_length=16, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='verblijfsobjectpandrelatie',
            name='id',
            field=models.CharField(max_length=31, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='code',
            field=models.CharField(max_length=5, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='naam_ptt',
            field=models.CharField(max_length=17, null=True),
        ),
    ]
