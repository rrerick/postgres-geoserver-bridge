from django.http import HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from user_profile.pg_user import PGControl
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from pool.connection_manager import Geoserver_Db
# Create your views here.


class AuthModelMixIn():
    """AuthView
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]


class RedirectRetriewView(AuthModelMixIn, APIView):
    """AuthView - After login the user is going to be redirected to here.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }

        if request.user:
            instance = PGControl.retrieve_data()
            validator = True
            while validator:

                user_info, instance2, actual_generator = PGControl.manager_information(
                    instance
                )

                if user_info:
                    print('Connection With the user: %s' % user_info)

                    try:

                        is_ok = Geoserver_Db.manager_db_with_geoserver(
                            user_info,
                            instance2
                        )

                        if not is_ok:
                            return HttpResponse("Don't Finished")
                        elif "TABLE DOESN'T EXISTS IN THIS DATABASE" in is_ok:
                            response = is_ok + ' - ' + str(instance2)
                            return HttpResponse(response)
                        else:
                            continue

                    except StopIteration:
                        validator = False
                return HttpResponse('<p><b>Finished -- You could verificate on the log file</b></p>')
        else:
            return Response(content)
