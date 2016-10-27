import os
import mimetypes
from django.test import TestCase
from unittest import skip


from ..objectstore  import ObjectStore


class TestObjectstore(TestCase):

    def setUp(self):
        self.objectstore = ObjectStore('BAG')

    @skip('Check auth')
    def test_objects(self):

        # clean up
        stored_objects = self.objectstore._get_full_container_list([])
        for ob in stored_objects:
            if ob['name'].startswith('bagtest/'):
                self.objectstore.delete_from_objectstore(ob['name'])

        res = self.objectstore._get_full_container_list([])
        self.assertEqual(len(res), 7)

        objects = ['diva/bag/{}'.format(filename) for filename in os.listdir('diva/bag')]
        self.assertEqual(len(objects), 29)

        for ob in objects:
            ob_name = ob.split('/')[-1]
            content = open(ob, 'rb').read()
            content_type = mimetypes.MimeTypes().guess_type(ob)[0]
            if not content_type:
                content_type = "application/octet-stream"
            self.objectstore.put_to_objectstore('bagtest/{}'.format(ob_name), content, content_type)

        res = self.objectstore._get_full_container_list([])
        self.assertEqual(len(res), 36)
