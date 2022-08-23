from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .database_connection import GEOSERVER_DB
# Create your views here.

def connection_geoserver_db(request):
    """Request from postgresql, to connection with database and if possible
    create,in GeoServer, the workspace

    Args;
        request (get)
    """

    reponse_db = GEOSERVER_DB.manager_db_with_geoserver()

    return HttpResponse ("ok")