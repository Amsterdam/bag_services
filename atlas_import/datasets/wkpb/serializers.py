from rest_framework import serializers

from . import models
from datasets.generic import rest


class Broncode(rest.HALSerializer):
    class Meta:
        model = models.Broncode
        fields = (
            '_links',
            'code',
            'omschrijving',
        )


class BroncodeDetail(rest.HALSerializer):
    documenten = rest.RelatedSummaryField()
    class Meta:
        model = models.Broncode
        fields = (
            '_links',
            'code',
            'omschrijving',
            'documenten',
        )


class Brondocument(rest.HALSerializer):
    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
            'documentnummer',
            'documentnaam',
        )


class BrondocumentDetail(rest.HALSerializer):
    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
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
    class Meta:
        model = models.Beperking
        fields = (
            '_links',
            'inschrijfnummer',
        )


class BeperkingDetail(rest.HALSerializer):
    beperkingtype = Beperkingcode()
    kadastrale_objecten = rest.RelatedSummaryField()

    class Meta:
        model = models.Beperking
        fields = (
            '_links',
            'inschrijfnummer',
            'beperkingtype',
            'datum_in_werking',
            'datum_einde',
            'kadastrale_objecten',
            'documenten'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('format') == 'html':
            self.fields.pop('kadastrale_objecten')


