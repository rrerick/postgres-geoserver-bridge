from .models import Pg_User
import jwt
import os
from django.core.exceptions import ObjectDoesNotExist

"""THIS CLASS IS RESPONSIBLE FOR TAKE CONTROL ABOUT ALL POSTGRESQL USERS 
"""


class PGControl():

    @staticmethod
    def manager_information(instance):
        """master of information
        RETURN:
            instance(): about database information
            decrypted_password : about password
        """

        try:
            instance_object = next(instance)
            print('user: ', instance_object)
            my_secret = os.getenv('secret')
            values = jwt.decode(
                instance_object.authtk,
                key=my_secret,
                algorithms=['HS256']
            )

            return values, instance_object, instance
        except StopIteration:
            print("ERROR: DATABASES IN THE END")
            return None, None, None

    @classmethod
    def retrieve_data(cls):
        """METHOD to retrieve data from Pg_user and Db_info Tables,
        corresponding to the authenticate user

        Args:
            param (instance) : information about user
        Return:
            user_info (generator) : a couple of information (database and postgres user to login)

        """
        count = 1
        while True:
            try:
                instance = Pg_User.objects.get(id=count)
                count += 1
                print(instance)
                yield instance
            except ObjectDoesNotExist:
                print('ERROR: DATABASE INFO WITH PK %s DOES NOT EXISTS' % (count))
                break
