from django.contrib import admin

from . import models

class ReadOnlyAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + [field.name for field in obj._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CodeOmschrijvingAdmin(ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')

class BeperkingAdmin(ReadOnlyAdmin):
    list_display = ('inschrijfnummer', 'beperkingtype')


admin.site.register(models.Beperkingcode, CodeOmschrijvingAdmin)
admin.site.register(models.Broncode, CodeOmschrijvingAdmin)
admin.site.register(models.Beperking, BeperkingAdmin)