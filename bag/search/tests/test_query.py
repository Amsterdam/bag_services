from rest_framework.test import APITransactionTestCase

from search.tests.fill_elastic import load_docs


class QueryTest(APITransactionTestCase):
    """
    Testing commonly used datasets
    """

    formats = [
        ('api', 'text/html; charset=utf-8'),
        ('json', 'application/json'),
        ('xml', 'application/xml; charset=utf-8'),
        ('csv', 'text/csv; charset=utf-8'),
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_docs(cls)

    def test_openbare_ruimte(self):
        response = self.client.get(
            "/atlas/search/openbareruimte/", {'q': "Prinsengracht"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        # self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['naam'], "Prinsengracht")

        self.assertEqual(
            response.data['results'][0]['subtype'], "water")

    def test_subject(self):
        """
        We are not authorized. should fail
        """
        response = self.client.get(
            "/atlas/search/kadastraalsubject/", {'q': "kikker"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('results', response.data)

    def test_bouwblok(self):
        response = self.client.get(
            "/atlas/search/bouwblok/", {'q': "RN3"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['code'], "RN35")

    def test_adres(self):
        response = self.client.get(
            "/atlas/search/postcode/", {'q': "1016 SZ 228 a 1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        # not due to elk scoring it could happen 228 B, scores better
        # then 228 A
        adres = response.data['results'][0]['adres']
        self.assertTrue(adres.startswith("Rozenstraat 228"))
        self.assertFalse(expr='order' in response.data['results'][0],
                         msg='Order data should be stripped from result')

    # def test_postcode_exact(self):
    #    response = self.client.get(
    #        "/search/postcode/", {'q': "1016 SZ 228 a 1"})
    #    self.assertEqual(response.status_code, 200)

    #    # now due to elk scoring it could happen 228 B, scores better
    #    # then 228 A

    #    adres = response.data['adres']
    #    self.assertTrue(
    #        adres.startswith("Rozenstraat 228")
    #    )

    #def test_postcode_exact_incorrect_house_num(self):
    #    response = self.client.get(
    #        "/search/postcode/", {'q': "1016 SZ 1"})
    #    self.assertEqual(response.status_code, 200)

    #    self.assertNotIn('adres', response.data)

    #def test_postcode_exact_no_house_num(self):
    #    response = self.client.get(
    #        "/search/postcode/", {'q': "1016 SZ"})
    #    self.assertEqual(response.status_code, 200)

    #    # we should get openbare ruimte
    #    self.assertNotIn('adres', response.data)

    # /typeahead/logica

    # /atlas/typeahead/gebieden/
    # /atlas/typeahead/brk/
    # /atlas/typeahead/bag/

    def test_typeahead_gebied(self):
        response = self.client.get(
            "/atlas/typeahead/gebieden/", {'q': "Centrum"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Centrum', str(response.data))

    def test_typeahead_bag_postcode(self):

        response = self.client.get(
            "/atlas/typeahead/bag/", {'q': "1016 SZ"})
        self.assertEqual(response.status_code, 200)

        self.assertIn('Rozenstraat', str(response.data))

    def test_typeahead_bag_adres(self):

        for fmt, content_type in self.formats:

            url = "/atlas/typeahead/bag/"
            response = self.client.get(
                url, {'q': "Rozenstraat 228", 'format': fmt})

            self.assertEqual(
                f"{content_type}",
                response["Content-Type"],
                "Wrong Content-Type for {}".format(url),
            )

            self.assertEqual(response.status_code, 200)

            self.assertIn('Rozenstraat 228', str(response.data))

    def test_typeahead_bag_openbare_ruimte(self):

        for fmt, content_type in self.formats:

            url = "/atlas/typeahead/bag/"
            response = self.client.get(
                url, {'q': "Rozenstraat", 'format': fmt})

            self.assertEqual(
                f"{content_type}",
                response["Content-Type"],
                "Wrong Content-Type for {}".format(url),
            )

            self.assertEqual(response.status_code, 200)

            self.assertIn('Rozenstraat', str(response.data))

    def test_typeahead_subject(self):
        """
        We are not authorized. should fail
        """
        response = self.client.get(
            "/atlas/typeahead/brk/", {'q': "kikker"})
        self.assertEqual(response.status_code, 200)

        self.assertNotIn('kikker', str(response.data))

    def test_bouwblok_typeahead(self):

        response = self.client.get(
            "/atlas/typeahead/bag/", {'q': "RN35"})
        self.assertEqual(response.status_code, 200)

        self.assertIn("RN35", str(response.data))

    def test_typeahead_landelijk_id_na(self):
        q = self.na.landelijk_id[0:9]
        res = self.client.get(f'/atlas/typeahead/bag/?q={q}')
        self.assertEquals(200, res.status_code)
        self.assertEquals(f'bag/verblijfsobject/{self.na.verblijfsobject.landelijk_id}/', res.data[0]['content'][0]['uri'])

    def test_typeahead_adresseerbaar_object_id_na(self):
        adresseerbaar_object_id = self.na.verblijfsobject.landelijk_id
        q = adresseerbaar_object_id.lstrip('0')[0:9]
        res = self.client.get(f'/atlas/typeahead/bag/?q={q}')
        self.assertEquals(200, res.status_code)
        self.assertEquals(f'bag/verblijfsobject/{adresseerbaar_object_id}/', res.data[0]['content'][0]['uri'])

    def test_typeahead_opr_landelijk_id(self):
        q = self.prinsengracht.landelijk_id[0:6]
        res = self.client.get(f'/atlas/typeahead/gebieden/?q={q}')
        self.assertEquals(200, res.status_code)
        self.assertEquals(f'bag/openbareruimte/{self.prinsengracht.landelijk_id}/', res.data[0]['content'][0]['uri'])

    def test_typeahead_pand_landelijk_id(self):
        q = self.pand1.landelijk_id[0:9]
        res = self.client.get(f'/atlas/typeahead/bag/?q={q}')
        self.assertEquals(200, res.status_code)
        self.assertEquals(f'bag/pand/{self.pand1.landelijk_id}/', res.data[0]['content'][0]['uri'])

    def test_typeahead_pand_pandnaam(self):
        q = self.pand1.pandnaam[0:6]
        res = self.client.get(f'/atlas/typeahead/bag/?q={q}')
        self.assertEquals(200, res.status_code)
        self.assertEquals(f'bag/pand/{self.pand1.landelijk_id}/', res.data[0]['content'][0]['uri'])

