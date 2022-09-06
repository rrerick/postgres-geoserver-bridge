from .models import Pg_User
from cryptography.fernet import Fernet
from django.core.exceptions import ObjectDoesNotExist

"""THIS CLASS IS RESPONSIBLE FOR TAKE CONTROL ABOUT ALL POSTGRESQL USERS 
"""

class PGControl():

    @staticmethod
    def manager_information():
        """master of information
        RETURN:
            instance(): about database information
            decrypted_password : about password
        """

        instance = PGControl.retrieve_data()
        try:
            instance = next(instance)
            print(instance)
            f = Fernet(instance.pub_key)
            decrypted_password = f.decrypt(instance.token.encode())
            print(decrypted_password.decode())
            return instance, decrypted_password.decode()
        except StopIteration:
            print ("ERROR: DATABASES IN THE END")
            return None, None

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
                yield instance
            except ObjectDoesNotExist:
                print('ERROR: DATABASE INFO WITH PK %s DOES NOT EXISTS' %(count))
                break


