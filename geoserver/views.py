import re
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from user_profile.pg_user import PGControl
from rest_framework.response import Response
from django.contrib.auth import authenticate
from user_profile.tokens_keys import TokenEngineer
from .database_connection import GEOSERVER_DB
# Create your views here.


class RedirectRetriewView(APIView):
    """AuthView - After login the user is going to be redirected to here.
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        if request.user:
            validator = True
            # (generator)It'll process the password and the user of geoverser, linked on this profile
            responses = TokenEngineer.process_information(request)
            while validator:

                try:

                    response = next(responses)
                    print(response)

                    # Here we going to get information about Postgres user and DB
                    user_info, db_info, decrypted_password = PGControl.manager_information(
                        request)
                    print(user_info, db_info)
                    if response:
                        workspace_create = GEOSERVER_DB.manager_db_with_geoserver(
                            response, user_info, db_info, decrypted_password)
                        print("Verification: Done!")
                    else:
                        continue
                except StopIteration:
                    validator = False

            return HttpResponse('Done!')
        else:
            return Response(content)


