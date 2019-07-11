from django.db import models, connection


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

    @classmethod
    def get_or_create(cls, omschrijving):
        try:
            created = False
            obj = cls.objects.get(omschrijving=omschrijving)
        except cls.DoesNotExist:
            # Create new code
            table = cls._meta.db_table
            with connection.cursor() as cursor:
                query = f'''
            SELECT COALESCE(MAX(CASE WHEN code ~ '^[0-9]+$' THEN code::INTEGER ELSE 0 END), 0) FROM {table}
                    '''
                cursor.execute(query)
                (max_code,) = cursor.fetchone()
                obj = cls(code=str(max_code + 1), omschrijving=omschrijving)
                obj.save()
                created = True
        return obj, created
