from .models import Pg_User, Db_info
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.core.exceptions import ObjectDoesNotExist

"""
ESTA CLASSE SERVE PARA PEGAR INFORMAÇÕES DE CONEXÃO
E RETORNAR O USUARIO E BANCO CORRESPONDENTE
"""

class PGControl():

    @staticmethod
    def manager_information(request):
        """master of information
        """

        user_info, db_info, decrypted_password = PGControl.retrieve_data(request)

        return user_info, db_info, decrypted_password

    @classmethod
    def retrieve_data(cls, param):
        """METHOD to retrieve data from Pg_user and Db_info Tables,
        corresponding to the authenticate user

        Args:
            param (instance) : information about user
        Return:
            user_info (instance) : a couple of information (database and postgres user to login)
            db_info (instance): database information
            decrypt_password : password to use when connect database
        """

        user_info = Pg_User.objects.get(owner=param.user)
        f = Fernet(user_info.pub_key)
        decrypt_password = f.decrypt(user_info.token.encode())
        try:
            db_info = Db_info.objects.get(
                pg_user_name = user_info.id
            )
        except ObjectDoesNotExist:
            db_info = None

        finally:

            return user_info, db_info, decrypt_password.decode()