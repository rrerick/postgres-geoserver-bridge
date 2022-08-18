from django.http import JsonResponse
from django.shortcuts import render
from .database_connection import GEOSERVER_DB
# Create your views here.

def connection_geoserver_db(request):
    """Request from postgresql, to connection with database and if possible
    create,in GeoServer, the workspace

    Args;
        request (get)
    """

    reponse_db = GEOSERVER_DB.database_connection()

    return JsonResponse(reponse_db[0], safe=False)