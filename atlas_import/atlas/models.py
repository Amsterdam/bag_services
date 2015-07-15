from django.db import models


class StatusMixin(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Bron(StatusMixin, models.Model):

    code = models.CharField(max_length=4, primary_key=True)
    omschrijving = models.CharField(max_length=150)
