from django.contrib import admin
from datasets.generic import admin_mixins

from . import models

class SoortCultuurOnbebouwdDomeinAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')


class BebouwingscodeDomeinAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')


class KadastraalObjectAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'gemeentecode_domein', 'sectie', 'perceelnummer', 'objectindex_letter', 'objectindex_nummer')


admin.site.register(models.SoortCultuurOnbebouwdDomein, SoortCultuurOnbebouwdDomeinAdmin)
admin.site.register(models.BebouwingscodeDomein, BebouwingscodeDomeinAdmin)
admin.site.register(models.KadastraalObject, KadastraalObjectAdmin)
