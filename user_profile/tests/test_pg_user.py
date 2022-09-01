from django.contrib.auth.models import User
from django.test import TestCase
from user_profile.models import create_pg_user,Pg_User,Db_info
from cryptography.fernet import Fernet
import psycopg2
from psycopg2.extras import RealDictCursor

class TestPgUserFile(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username='funai',
            email = None,
            password='1234'
        )
        self.object_test1 = create_pg_user.objects.create(
            owner = user,
            username = 'postgres',
            password = 'postgres',
        )
        self.user = Pg_User.objects.get(username='postgres')
        self.object_test2 = Db_info.objects.create(
            pg_user_name = self.user,
            dbname = 'atlante',
            ip = 'localhost',
            port = '5432'
        )
        
        self.object_test2.save()
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

        user_info = self.user
        f = Fernet(user_info.pub_key)
        decrypt_password = f.decrypt(user_info.token.encode())
        self.assertTrue(decrypt_password.decode())

        db_info = Db_info.objects.get(
            pg_user_name = user_info
        )

        self.assertTrue(db_info)

    def test_connection_with_retrieve_data(self):
        """Test to validate the conection with paramters
        in DB
        """

        user_info = self.user

        f = Fernet(user_info.pub_key)
        decrypt_password = f.decrypt(user_info.token.encode())

        db_info = Db_info.objects.get(
            pg_user_name = user_info
        )

        connec = psycopg2.connect(
            database=db_info.dbname,
            user=user_info.username,
            password=decrypt_password.decode(),
            host=db_info.ip,
            port=db_info.port
        )

        self.assertTrue(connec)
        curs = connec.cursor(cursor_factory=RealDictCursor)
        curs.execute(
            "SELECT metadata, object_name FROM _v_metadata_catalog"
        )

        json_field = {}
        count = 0
        for record in curs:
            json_field[count] = dict(record)
            count += 1


        curs.close()
        self.assertIsNotNone(json_field)