def download_datafiles():
    pass


def import_blah_file():
    pass


class ImportJob(object):

    name = "atlas-import"

    def tasks(self):
        return [
            download_datafiles,
            import_blah_file,
        ]
