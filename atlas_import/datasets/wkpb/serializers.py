from rest_framework import serializers

from . import models
from datasets.generic import rest


class Beperkingcode(serializers.ModelSerializer):
    class Meta:
        model = models.Beperkingcode
        fields = (
            'code',
            'omschrijving',
        )


class Brondocument(rest.HALSerializer):
    class Meta:
        model = models.Brondocument
        fields = (
            'documentnaam',
            'url'
        )


class Beperking(rest.HALSerializer):
    beperkingtype = Beperkingcode()
    documenten = Brondocument(many=True)

    class Meta:
        model = models.Beperking
        fields = (
            '_links',
            'inschrijfnummer',
            'beperkingtype',
            'datum_in_werking',
            'datum_einde',
            'documenten'
        )


class BeperkingKadastraalObject(rest.HALSerializer):
    beperking = Beperking()

    class Meta:
        model = models.BeperkingKadastraalObject
        fields = (
            '_links',
            'beperking',
        )
