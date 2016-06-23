from django.core.management import BaseCommand

from datasets.bag.models import Verblijfsobject
from datasets.brk.models import KadastraalObject


class Command(BaseCommand):
    """
    Test script for looking up related kot models for a verblijfsobject
    """
    def handle(self, *args, **options):
        vbo = Verblijfsobject.objects.get(pk='03630000749400')

        kot_models = vbo.kadastrale_objecten.all()

        for kot in kot_models:
            apercelen, gpercelen = [], []
            pk = kot.id

            if kot.indexletter == 'G':
                apercelen = [m.pk for m in kot.a_percelen.all()]
            else:
                gpercelen = [m.pk for m in kot.g_percelen.all()]

            # keep fetching items until nothing new is found
            while True:
                new_a = [m.pk for m in self.get_apercelen(gpercelen, apercelen)]
                new_g = [m.pk for m in self.get_gpercelen(apercelen, gpercelen)]

                if not len(new_a) and not len(new_g):
                    break

                apercelen += new_a
                gpercelen += new_g

            print('%s has %d a-percelen' % (pk, len(apercelen)))
            for pk in apercelen:
                print(' - %s' % pk)

            print('%s has %d g-percelen' % (pk, len(gpercelen)))
            for pk in gpercelen:
                print(' - %s' % pk)

    def get_apercelen(self, gpercelen_pks, exclude_pks):
        return KadastraalObject\
            .objects\
            .filter(indexletter='A', g_percelen__pk__in=gpercelen_pks)\
            .exclude(pk__in=exclude_pks)

    def get_gpercelen(self, apercelen_pks, exclude_pks):
        return KadastraalObject\
            .objects\
            .filter(indexletter='G', a_percelen__pk__in=apercelen_pks)\
            .exclude(pk__in=exclude_pks)


"""
NL.KAD.OnroerendeZaak.11460857510001 has 3 a-percelen
 - NL.KAD.OnroerendeZaak.11460857510001
 - NL.KAD.OnroerendeZaak.11460857510002
 - NL.KAD.OnroerendeZaak.11460857510003
NL.KAD.OnroerendeZaak.11460857510003 has 1 g-percelen
 - NL.KAD.OnroerendeZaak.11460614770000
NL.KAD.OnroerendeZaak.11460857510002 has 3 a-percelen
 - NL.KAD.OnroerendeZaak.11460857510001
 - NL.KAD.OnroerendeZaak.11460857510002
 - NL.KAD.OnroerendeZaak.11460857510003
NL.KAD.OnroerendeZaak.11460857510003 has 1 g-percelen
 - NL.KAD.OnroerendeZaak.11460614770000
NL.KAD.OnroerendeZaak.11460857510003 has 3 a-percelen
 - NL.KAD.OnroerendeZaak.11460857510001
 - NL.KAD.OnroerendeZaak.11460857510002
 - NL.KAD.OnroerendeZaak.11460857510003
NL.KAD.OnroerendeZaak.11460857510003 has 1 g-percelen
 - NL.KAD.OnroerendeZaak.11460614770000
 """
