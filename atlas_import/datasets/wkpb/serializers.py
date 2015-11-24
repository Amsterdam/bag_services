from rest_framework import serializers

from . import models
from datasets.generic import rest


class Broncode(rest.HALSerializer):
    _display = rest.DisplayField()
    class Meta:
        model = models.Broncode
        fields = (
            '_links',
            '_display',
            'code',
            'omschrijving',
        )


class BroncodeDetail(rest.HALSerializer):
    _display = rest.DisplayField()
    documenten = rest.RelatedSummaryField()
    class Meta:
        model = models.Broncode
        fields = (
            '_links',
            '_display',
            'code',
            'omschrijving',
            'documenten',
        )


class Brondocument(rest.HALSerializer):
    _display = rest.DisplayField()
    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
            '_display',
            'documentnummer',
            'documentnaam',
        )


class BrondocumentDetail(rest.HALSerializer):
    _display = rest.DisplayField()
    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
            '_display',
            'documentnummer',
            'bron',
            'documentnaam',
            'persoonsgegeven_afschermen',
            'soort_besluit',
            'url',
            'beperking'
        )


class Beperkingcode(serializers.ModelSerializer):
    class Meta:
        model = models.Beperkingcode
        fields = (
            'code',
            'omschrijving',
        )


class Beperking(rest.HALSerializer):
    _display = rest.DisplayField()
    class Meta:
        model = models.Beperking
        fields = (
            '_links',
            '_display',
            'inschrijfnummer',
        )


class BeperkingDetail(rest.HALSerializer):
    _display = rest.DisplayField()
    beperkingtype = Beperkingcode()
    kadastrale_objecten = rest.RelatedSummaryField()

    class Meta:
        model = models.Beperking
        fields = (
            '_links',
            '_display',
            'inschrijfnummer',
            'beperkingtype',
            'datum_in_werking',
            'datum_einde',
            'kadastrale_objecten',
            'documenten'
        )



