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


class Brondocument(rest.HALSerializer):
    _display = rest.DisplayField()
    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
            '_display',
            'url',
            'documentnummer',
            'documentnaam',
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


class BrondocumentDetail(rest.HALSerializer):
    _display = rest.DisplayField()
    beperking = Beperking()
    bron = Broncode()

    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
            '_display',
            'inschrijfnummer',
            'bron',
            'inschrijfnummer',
            'persoonsgegeven_afschermen',
            'soort_besluit',
            'url',
            'beperking'
        )


class BeperkingDetail(rest.HALSerializer):
    _display = rest.DisplayField()
    beperkingtype = Beperkingcode()
    kadastrale_objecten = rest.RelatedSummaryField()
    documenten = rest.RelatedSummaryField()

    class Meta:
        model = models.Beperking
        fields = (
            '_links',
            '_display',
            'id',
            'inschrijfnummer',
            'beperkingtype',
            'datum_in_werking',
            'datum_einde',
            'kadastrale_objecten',
            'documenten'
        )

    # TODO handle this smarter
    def to_representation(self, instance):
        data = super(BeperkingDetail, self).to_representation(instance)

        data['beperkingcode'] = data['beperkingtype']
        del data['beperkingtype']

        return data

    def get_beperkingcode(self, obj):
        return Beperkingcode(source='*')
