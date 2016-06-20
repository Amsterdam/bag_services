# Python
import datetime
from unittest.mock import Mock
# Packages
from django.http import HttpResponse
from corsheaders.middleware import CorsMiddleware
from rest_framework.test import APITestCase


class PanoramaApiTest(APITestCase):

    def test_cors(self):
        """
        Cross Origin Requests should be allowed.
        """
        request = Mock(path='https://api.datapunt.amsterdam.nl/brk/object')
        request.method = 'GET'
        request.is_secure = lambda: True
        request.META = {
            'HTTP_REFERER': 'https://foo.google.com',
            'HTTP_HOST': 'api.datapunt.amsterdam.nl',
            'HTTP_ORIGIN': 'https://foo.google.com',
        }
        response = CorsMiddleware().process_response(request, HttpResponse())
        self.assertTrue('access-control-allow-origin' in response._headers)
        self.assertEquals('*', response._headers['access-control-allow-origin'][1])

