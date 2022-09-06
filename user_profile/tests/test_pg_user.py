from django.test import TestCase
from user_profile.models import create_pg_user,Pg_User
from django.core.exceptions import ObjectDoesNotExist
from cryptography.fernet import Fernet


class TestPgUserFile(TestCase):

    def setUp(self):

        self.object_test1 = create_pg_user.objects.create(
            username = 'docker',
            password = 'docker',
            dbname='geoserver',
            ip = 'localhost',
            port = '5432'
        )
        self.object_test1.save()


    def test_retrive_data(self):
        """TEST to validate the retrieve data function
            (
            METHOD to retrieve data from Pg_user and Db_info Tables,
            corresponding to the authenticate user

            Args:
                param (instance) : information about user
            Return:
                pg_connection (dict) : a couple of information (database and user to login)
            )
        """
        count = 1
        while True:
            try:
                instance = Pg_User.objects.get(id=count)

                self.assertEquals(instance.dbname, 'geoserver' )
                f = Fernet(instance.pub_key)
                print(f.decrypt(instance.token.encode()))
                count += 1
            except ObjectDoesNotExist:
                print('ERROR: DATABASE INFO WITH PK %s DOES NOT EXISTS' %(count))
                break


