from timeit import repeat
from turtle import get_poly
from django.test import TestCase
from ..models import  UsersGeoserver, Token
from django.contrib.auth.models import User, UserManager
from cryptography.fernet import Fernet
# Create your tests here.
class UsersProfileTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username='test',
            email = None,
            password='1234'
        )
        self.objects = UsersGeoserver.objects.create(
            owner = user,
            geoserver_ip = '0.0.0.0',
            geoserver_user = 'admin',
            geoserver_password = 'geoserver',
            repeat_password = 'geoserver',
        )
        self.object = Token.objects.get()
        self.objects.save()
    def test_to_get_token_passwd(self):
        """TEST to retrieve password's token and decrypt message
        """


        f = Fernet(self.object.pub_key)
        response = f.decrypt(self.object.token.encode())
        self.assertTrue(response)

    def test_to_connect_geoserver(self):
        """TEST to connect with geoserver using token params
        """

        from geo.Geoserver import Geoserver
        f = Fernet(self.object.pub_key)
        response = f.decrypt(self.object.token.encode())

        connect = Geoserver(
            "http://localhost:8080/geoserver",
            username=self.objects.geoserver_user,
            password=response
        )

        self.assertTrue(connect)