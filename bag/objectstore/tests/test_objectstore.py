import mimetypes
import os
from unittest import skipIf, skip

from django.conf import settings
from django.test import TestCase



class TestObjectstore(TestCase):
    @skipIf(settings.NO_INTEGRATION_TEST, 'blabla')
    @skip('Check auth')
    def test_objects(self):

        # clean up old cruft
        stored_objects = self.objectstore._get_full_container_list([])
        for ob in stored_objects:
            if ob['name'].startswith('bagtest/'):
                self.objectstore.delete_from_objectstore(ob['name'])

        objects = ['diva/bag/{}'.format(filename)
                   for filename in os.listdir('diva/bag')]

        names = set()

        # upload test data
        for ob in objects:
            ob_name = ob.split('/')[-1]
            names.add(ob_name)
            content = open(ob, 'rb').read()
            content_type = mimetypes.MimeTypes().guess_type(ob)[0]
            if not content_type:
                content_type = "application/octet-stream"
            self.objectstore.put_to_objectstore(
                'bagtest/{}'.format(ob_name), content, content_type)

        # check if we saw all test files
        res = self.objectstore._get_full_container_list([])
        for ob in res:
            ob_name = ob['name'].split('/')[-1]
            if ob_name in names:
                names.remove(ob_name)
        self.assertEqual(len(names), 0)
