from django.contrib import admin

from . import models
from datasets.generic import admin_mixins


class GemeenteAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('gemeentecode', 'gemeentenaam')


class KadastraleGemeenteAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'code',)


class KadastraalObjectAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'aanduiding')


class SectieAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'code')


admin.site.register(models.KadastraalObject, KadastraalObjectAdmin)
admin.site.register(models.Gemeente, GemeenteAdmin)
admin.site.register(models.KadastraleGemeente, KadastraleGemeenteAdmin)
admin.site.register(models.Sectie, SectieAdmin)
