from curses.ascii import HT
from django.http import JsonResponse, HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from user_profile.pg_user import PGControl
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .connection_manager import GEOSERVER_DB
# Create your views here.


class RedirectRetriewView(APIView):
    """AuthView - After login the user is going to be redirected to here.
    --- NEEDS TO CHANGE TO A TOKEN AUTH
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }

        if request.user:

            user_info, instance, actual_generator = PGControl.manager_information()
            if user_info:
                validator = True
                while validator:
                    print('Connection With the user: %s' % user_info)

                    try:
                        if user_info:
                            is_ok = GEOSERVER_DB.manager_db_with_geoserver(
                                user_info, instance)
                            if not is_ok:
                                return HttpResponse("Don't Finished")
                            else:
                                next(actual_generator)
                    except StopIteration:
                        validator = False
                return HttpResponse('Done')
            else:
                return HttpResponse('ERROR: Postgres user')
        else:
            return Response(content)
