from .models import Token
from django.core.exceptions import ObjectDoesNotExist
from cryptography.fernet import Fernet


class TokenEngineer():

    @staticmethod
    def process_information(request):
        """INFORMATION manager
        ARGS:
            request (instance) : request information
        RETURN:
           user_info (yield - dict) : user and password content (or none)
        """

        retrieve_data = TokenEngineer.retrieve_user_info(request)

        if retrieve_data:
            user_info = {}
            for count in range(len(retrieve_data)):

                pub_key = retrieve_data[count].get('pub_key')
                f = Fernet(pub_key)

                user_info['username'] = retrieve_data[count].get('user')
                token = retrieve_data[count].get('token')
                passwd = f.decrypt(token.encode())

                service_url = retrieve_data[count].get('ip')

                user_info['password'] = passwd
                user_info['ip'] = service_url

                yield user_info
        else:
            return retrieve_data



    @classmethod
    def retrieve_user_info(cls,params):
        """METHOD to see if the current user has a Geoserver's user registred,
            if not return None

        Args:
            params (request) : info about the requesition.
        Return:
            retrive_data (dict):Info about user registred in user's table
        """
        try:
            retrieve_data = Token.objects.filter(owner=params.user).values()
        except ObjectDoesNotExist:
            retrieve_data = None

        return retrieve_data
