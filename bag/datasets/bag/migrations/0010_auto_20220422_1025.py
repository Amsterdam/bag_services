# Generated by Django 2.2.27 on 2022-04-22 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0009_auto_20220208_0806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grootstedelijkgebied',
            name='gsg_type',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
