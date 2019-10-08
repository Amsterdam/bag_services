from batch import batch
from datasets.generic import database
from . import models


class CodeOmschrijvingDataTask(batch.BasicTask):
    model = None
    data = []

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        check_duplicates = set()
        for entry in self.data:
            if entry[1] in check_duplicates:
                raise ValueError(f"Duplicate omschrijving {entry[1]} in {type(self).__name__}")
            check_duplicates.add(entry[1])

        avrs = [self.process_row(entry) for entry in self.data]
        self.model.objects.bulk_create(avrs, batch_size=database.BATCH_SIZE)

    def process_row(self, r):
        # noinspection PyCallingNonCallable
        return self.model(pk=r[0], omschrijving=r[1])


class ImportToegangTask(CodeOmschrijvingDataTask):
    name = "Import Toegang"
    model = models.Toegang
    data = [
        ("01", "Trap"),
        ("02", "Galerij + trap"),
        ("03", "Lift"),
        ("04", "Galerij + lift"),
        ("05", "Centrale hal"),
        ("06", "Trap / centrale hal"),
        ("07", "Lift / centrale hal"),
        ("99", "Onbekend"),
        ("08", "Begane grond"),
    ]
