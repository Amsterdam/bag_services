from django.db import models


class ImportStatusMixin(models.Model):
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DocumentStatusMixin(models.Model):
    document_mutatie = models.DateField(null=True)
    document_nummer = models.CharField(max_length=20, null=True)

    class Meta:
        abstract = True


class GeldigheidMixin(models.Model):
    begin_geldigheid = models.DateField(null=True)
    einde_geldigheid = models.DateField(null=True)

    class Meta:
        abstract = True


class MutatieGebruikerMixin(models.Model):
    mutatie_gebruiker = models.CharField(max_length=30, null=True)

    class Meta:
        abstract = True


class CodeOmschrijvingMixin(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)

