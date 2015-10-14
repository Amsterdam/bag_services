from rest_framework import serializers

from . import models


class Beperkingcode(serializers.ModelSerializer):
    class Meta:
        model = models.Beperkingcode
        fields = (
            'code',
            'omschrijving',
        )


class Beperking(serializers.ModelSerializer):
    beperkingtype = Beperkingcode()

    class Meta:
        model = models.Beperking
        fields = (
            'inschrijfnummer',
            'beperkingtype',
            'datum_in_werking',
            'datum_einde',
            'documenten'
        )
