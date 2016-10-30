# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

ATLAS_CLIENT = 'atlas_client'
CLIENT_ID = 'KosSHb9BUhy2Jb8tt0Z4iNB0wlYvKGLyb9G3hG9X'


def create_atlas_client(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Application = apps.get_model('oauth2_provider', 'Application')

    owner = User.objects.create(username=ATLAS_CLIENT)
    Application.objects.create(
        client_id=CLIENT_ID,
        user=owner,
        client_type='public',
        authorization_grant_type='password',
        name=ATLAS_CLIENT,
    )


def remove_atlas_client(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Application = apps.get_model('oauth2_provider', 'Application')

    Application.objects.filter(client_id=CLIENT_ID).delete()
    User.objects.filter(username=ATLAS_CLIENT).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('oauth2_provider', '0002_08_updates'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(code=create_atlas_client,
                             reverse_code=remove_atlas_client)
    ]
