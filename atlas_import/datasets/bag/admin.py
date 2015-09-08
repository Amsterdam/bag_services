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


class BuurtAdmin(ReadOnlyAdmin):
    list_display = ('id', 'code', 'naam', 'stadsdeel')


class GemeenteAdmin(ReadOnlyAdmin):
    list_display = ('id', 'code', 'naam')


class LigplaatsAdmin(ReadOnlyAdmin):
    list_display = ('id', 'buurt', 'status')


class NummeraanduidingAdmin(ReadOnlyAdmin):
    list_display = ('id', 'adres', 'type', 'status')


class OpenbareRuimteAdmin(ReadOnlyAdmin):
    list_display = ('id', 'code', 'naam', 'type', 'status')


class PandAdmin(ReadOnlyAdmin):
    list_display = ('id', 'bouwjaar', 'status')


class StadsdeelAdmin(ReadOnlyAdmin):
    list_display = ('code', 'naam')


class StandplaatsAdmin(ReadOnlyAdmin):
    list_display = ('id', 'buurt', 'status')


class VerblijfsobjectAdmin(ReadOnlyAdmin):
    list_display = ('id', 'buurt', 'status', 'gebruiksdoel_omschrijving')


class WoonplaatsAdmin(ReadOnlyAdmin):
    list_display = ('code', 'naam')

# Register your models here.
admin.site.register(models.Bron, CodeOmschrijvingAdmin)
admin.site.register(models.Buurt, BuurtAdmin)
admin.site.register(models.Eigendomsverhouding, CodeOmschrijvingAdmin)
admin.site.register(models.Financieringswijze, CodeOmschrijvingAdmin)
admin.site.register(models.Gebruik, CodeOmschrijvingAdmin)
admin.site.register(models.Gemeente, GemeenteAdmin)
admin.site.register(models.Ligging, CodeOmschrijvingAdmin)
admin.site.register(models.Ligplaats, LigplaatsAdmin)
admin.site.register(models.LocatieIngang, CodeOmschrijvingAdmin)
admin.site.register(models.Nummeraanduiding, NummeraanduidingAdmin)
admin.site.register(models.OpenbareRuimte, OpenbareRuimteAdmin)
admin.site.register(models.Pand, PandAdmin)
admin.site.register(models.RedenAfvoer, CodeOmschrijvingAdmin)
admin.site.register(models.Stadsdeel, StadsdeelAdmin)
admin.site.register(models.Standplaats, StandplaatsAdmin)
admin.site.register(models.Status, CodeOmschrijvingAdmin)
admin.site.register(models.Toegang, CodeOmschrijvingAdmin)
admin.site.register(models.Verblijfsobject, VerblijfsobjectAdmin)
admin.site.register(models.Woonplaats, WoonplaatsAdmin)
