from django.contrib import admin

from . import models
from datasets.generic import admin_mixins


class CodeOmschrijvingAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')


class BuurtAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'code', 'naam', 'stadsdeel')


class GemeenteAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'code', 'naam')


class LigplaatsAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'buurt', 'status')


class NummeraanduidingAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'adres', 'type', 'status')


class OpenbareRuimteAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'code', 'naam', 'type', 'status')


class PandAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'bouwjaar', 'status')


class StadsdeelAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'naam')


class StandplaatsAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'buurt', 'status')


class VerblijfsobjectAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'buurt', 'status', 'gebruiksdoel_omschrijving')


class WoonplaatsAdmin(admin_mixins.ReadOnlyAdmin):
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
