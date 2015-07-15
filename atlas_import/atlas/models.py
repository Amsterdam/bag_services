from django.db import models


class ImportStatusMixin(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Bron(ImportStatusMixin, models.Model):

    code = models.CharField(max_length=4, primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)


class Status(ImportStatusMixin, models.Model):

    code = models.CharField(max_length=4, primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)


class Gemeente(ImportStatusMixin, models.Model):

    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=40)
    verzorgingsgebied = models.BooleanField(default=False)
    vervallen = models.BooleanField(default=False)


class Stadsdeel(ImportStatusMixin, models.Model):

    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.BooleanField(default=False)
    gemeente = models.ForeignKey(Gemeente)


class Buurt(ImportStatusMixin, models.Model):

    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.BooleanField(default=False)
    stadsdeel = models.ForeignKey(Stadsdeel)


class Ligplaats(ImportStatusMixin, models.Model):

    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.DecimalField(max_digits=14, decimal_places=0, unique=True)
    ligplaats_nummer = models.DecimalField(max_digits=10, decimal_places=0, unique=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    buurt = models.ForeignKey(Buurt, null=True)