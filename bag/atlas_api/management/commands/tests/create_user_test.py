import datetime
from ..import_users import Command
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.utils.timezone import UTC

USERNAME = 'passwordless_testuser'

class TestCreateUser(APITestCase):
    management_command = Command()

    def test_create_user(self):
        Command().create_user(USERNAME, datetime.datetime.strptime('05-04-1999', "%d-%m-%Y").replace(tzinfo=UTC()))
        testuser = User.objects.filter(username=USERNAME)[0]
        self.assertEqual(testuser.username, USERNAME)
        self.assertTrue(testuser.has_perm('brk.view_sensitive_details'))
