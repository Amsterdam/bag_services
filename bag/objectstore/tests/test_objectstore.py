import mimetypes
import os
from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from objectstore import objectstore


class TestObjectstore(TestCase):

    @skipIf(settings.NO_INTEGRATION_TEST, 'Pass integration tests')
    def test_objects(self):

        container_name = 'Diva'
        # clean up old cruft
        stored_objects = objectstore.get_full_container_list(container_name)
        for ob in stored_objects:
            if ob['name'].startswith('bagtest/'):
                objectstore.delete_from_objectstore(container_name, ob['name'])

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

            objectstore.put_to_objectstore(
                container_name, 'bagtest/{}'.format(ob_name),
                content, content_type)

        # check if we saw all test files
        res = objectstore.get_full_container_list(container_name)
        for ob in res:
            ob_name = ob['name'].split('/')[-1]
            if ob_name in names:
                names.remove(ob_name)
        self.assertEqual(len(names), 0)
