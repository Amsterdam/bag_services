from rest_framework.generics import RetrieveAPIView

from . import models, serializers


class BeperkingKadastraalObjectView(RetrieveAPIView):
    serializer_class = serializers.Beperking
    lookup_field = 'kadastraal_object_akr'
    queryset = models.BeperkingKadastraalObject.objects.all()

    def get_object(self):
        bko = super(BeperkingKadastraalObjectView, self).get_object()

        return bko.beperking
