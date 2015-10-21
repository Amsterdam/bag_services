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


class Brondocument(rest.HALSerializer):
    bron = Broncode()

    class Meta:
        model = models.Brondocument
        fields = (
            '_links',
            'documentnummer',
            'bron',
            'documentnaam',
            'persoonsgegeven_afschermen',
            'soort_besluit',
            'url'
        )


class Beperkingcode(rest.HALSerializer):
    class Meta:
        model = models.Beperkingcode
        fields = (
            '_links',
            'code',
            'omschrijving',
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
            'kadastrale_objecten',
            'documenten'
        )


