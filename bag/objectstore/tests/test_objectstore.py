import mimetypes
import os
from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from objectstore import objectstore


class TestObjectstore(TestCase):
    def test_split_first(self):
        self.assertEqual("FRST", objectstore.split_first("FRST_File_Name.typ"))

    def test_split_second(self):
        self.assertEqual("File", objectstore.split_second("FRST_File_Name.typ"))

    def test_split_prefix(self):
        self.assertEqual("FRST_File", objectstore.split_prefix("FRST_File_Name.typ"))

    def test_concat_first_two(self):
        self.assertEqual("FRSTFile", objectstore.concat_first_two("FRST_File_Name.typ"))

    def test_folder_mapping(self):
        keys = objectstore.folder_mapping.keys()
        self.assertTrue('bag_actueel' in keys)
        self.assertTrue('bag_sleutel' in keys)
        self.assertTrue('bag_wkt' in keys)
        self.assertTrue('brk_ascii' in keys)
        self.assertTrue('brk_shp' in keys)
        self.assertTrue('gebieden_shp' in keys)
        self.assertTrue('bag_geometrie' in keys)
        self.assertTrue('wkpb_beperkingen' in keys)

        self.assertEqual('bag', objectstore.folder_mapping['bag_actueel'][0])
        self.assertEqual('bag', objectstore.folder_mapping['bag_sleutel'][0])
        self.assertEqual('bag_wkt', objectstore.folder_mapping['bag_wkt'][0])
        self.assertEqual('bag_wkt', objectstore.folder_mapping['bag_geometrie'][0])
        self.assertEqual('brk', objectstore.folder_mapping['brk_ascii'][0])
        self.assertEqual('brk_shp', objectstore.folder_mapping['brk_shp'][0])
        self.assertEqual('gebieden', objectstore.folder_mapping['gebieden_ascii'][0])
        self.assertEqual('gebieden_shp', objectstore.folder_mapping['gebieden_shp'][0])
        self.assertEqual('beperkingen', objectstore.folder_mapping['wkpb_beperkingen'][0])

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
                container_name, 'bagtest/{}'.format(ob_name), content, content_type)

        # check if we saw all test files
        res = objectstore.get_full_container_list(container_name)
        for ob in res:
            ob_name = ob['name'].split('/')[-1]
            if ob_name in names:
                names.remove(ob_name)
        self.assertEqual(len(names), 0)

    def test_select_last_created_files_split_first(self):

        f_split_first = [
            "BRK_20160101.ext", "BRK_20160201.ext", "BRK_20160301.ext", "BRK_20160401.ext", "BRK_20160501.ext",
            "BRK_20160601.ext", "BRK_20160701.ext", "BRK_20160801.ext", "BRK_20160901.ext", "BRK_20161001.ext",
            "BRK_20161101.ext", "ABC_20151123.ext"]

        res = objectstore.select_last_created_files(f_split_first)
        self.assertEqual(["ABC_20151123.ext", "BRK_20161101.ext"], res)

    def test_select_last_created_files_concat(self):

        f_concat = [
            "BRK_ABC_20160101.ext", "BRK_DEF_20160201.ext", "BRK_GHI_20160301.ext", "BRK_JKL_20160401.ext",
            "BRK_MNO_20160501.ext", "BRK_ABC_20160601.ext", "BRK_DEF_20160701.ext", "BRK_GHI_20160801.ext",
            "BRK_JKL_20160901.ext", "BRK_MNO_20161001.ext", "BRK_ABC_20161101.ext", "ABC_DEF_20151123.ext"]

        res = objectstore.select_last_created_files(f_concat, key_func=objectstore.concat_first_two)
        self.assertEqual(['ABC_DEF_20151123.ext',
                          'BRK_ABC_20161101.ext',
                          'BRK_DEF_20160701.ext',
                          'BRK_GHI_20160801.ext',
                          'BRK_JKL_20160901.ext',
                          'BRK_MNO_20161001.ext'], res)

    def test_select_last_created_files_prefix(self):

        f_split_prefix = [
            "BRK_ABC_20160101.ext", "BRK_DEF_20160201.ext", "BRK_GHI_20160301.ext", "BRK_JKL_20160401.ext",
            "BRK_MNO_20160501.ext", "BRK_ABC_20160601.ext", "BRK_DEF_20160701.ext", "BRK_GHI_20160801.ext",
            "BRK_JKL_20160901.ext", "BRK_MNO_20161001.ext", "BRK_ABC_20161101.ext", "ABC_DEF_20151123.ext"]

        res = objectstore.select_last_created_files(f_split_prefix, key_func=objectstore.split_prefix)
        self.assertEqual(['ABC_DEF_20151123.ext',
                          'BRK_ABC_20161101.ext',
                          'BRK_DEF_20160701.ext',
                          'BRK_GHI_20160801.ext',
                          'BRK_JKL_20160901.ext',
                          'BRK_MNO_20161001.ext'], res)

    def test_select_last_created_files_all(self):

        f_all = [
            "BRK_ABC_20160101.ext", "BRK_DEF_20160201.ext", "BRK_GHI_20160301.ext", "BRK_JKL_20160401.ext",
            "BRK_MNO_20160501.ext", "BRK_ABC_20160601.ext", "BRK_DEF_20160701.ext", "BRK_GHI_20160801.ext",
            "BRK_JKL_20160901.ext", "BRK_MNO_20161001.ext", "BRK_ABC_20161101.ext", "ABC_DEF_20151123.ext"]

        res = objectstore.select_last_created_files(f_all, key_func=objectstore.get_all)
        self.assertEqual(sorted(f_all), res)
