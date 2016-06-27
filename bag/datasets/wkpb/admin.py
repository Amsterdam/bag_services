from django.contrib import admin

from . import models
from datasets.generic import admin_mixins


class CodeOmschrijvingAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')


class BeperkingAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('inschrijfnummer', 'beperkingtype')


admin.site.register(models.Beperkingcode, CodeOmschrijvingAdmin)
admin.site.register(models.Broncode, CodeOmschrijvingAdmin)
admin.site.register(models.Beperking, BeperkingAdmin)
