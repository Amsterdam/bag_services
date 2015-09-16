from django.contrib import admin
from datasets.generic import admin_mixins

from . import models

class SoortCultuurOnbebouwdAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')


class BebouwingscodeAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('code', 'omschrijving')


class KadastraalObjectAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('id', 'gemeentecode', 'sectie', 'perceelnummer', 'objectindex_letter', 'objectindex_nummer')

class KadastraalSubjectAdmin(admin_mixins.ReadOnlyAdmin):
    list_display = ('subjectnummer', 'geslachtsnaam', 'naam_niet_natuurlijke_persoon')


admin.site.register(models.SoortCultuurOnbebouwd, SoortCultuurOnbebouwdAdmin)
admin.site.register(models.Bebouwingscode, BebouwingscodeAdmin)
admin.site.register(models.KadastraalObject, KadastraalObjectAdmin)
admin.site.register(models.KadastraalSubject, KadastraalSubjectAdmin)
