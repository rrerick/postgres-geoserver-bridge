"""
CONNECTION with database and get all metadata for creation purpose

Explain ideias:
    Connection with Database
    View the metadata field
    get information
    Separate Geoserver info

IP: 10.8.2.17
GeoServer
User: admin
Passwd: geoserver
Port: 8080
DB
User: postgres
Passwd: example
Port: 5410
"""
import os
import psycopg2
from psycopg2.errors import ConnectionException
from psycopg2.extras import RealDictCursor
from .serializers import GeoServerSerialization
from .models import INPEGeoserverCopy


class GEOSERVER_DB():
    cnect_database = None
    database_cursor = None
    json_fields = None

    @staticmethod
    def database_connection():
        """METHOD for connect with database (INPE) and serialize INTO django Database
        Returns:
            Query (dict/list)
        """
        try:
            cnect = psycopg2.connect(
                database=os.environ.get('dbname',),
                user=os.environ.get('user'),
                password=os.environ.get('password'),
                host=os.environ.get('host'),
                port=os.environ.get('port'),
            )

        except ConnectionException:
            cnect = None

        finally:
            if cnect != None:
                GEOSERVER_DB.database_cursor = cnect.cursor(
                    cursor_factory=RealDictCursor)
                GEOSERVER_DB.database_cursor.execute(
                    "SELECT metadata FROM _v_metadata_catalog")

                json_field = {}
                count = 0
                for record in GEOSERVER_DB.database_cursor:
                    json_field[count] = dict(record)
                    count += 1

                GEOSERVER_DB.serializer_response(json_field)
                GEOSERVER_DB.database_cursor.close()

                return json_field

            else:
                GEOSERVER_DB.database_cursor.close()
                return 'connection failure'

    @classmethod
    def serializer_response(cls, query):
        """METHOD for serialize, INPE database into APP database
        Args:
            query (dict) : Query response(dict form)
        """

        serializer_data = {}

        for count in range(len(query)):
            serializer_data['data'] = query[count]
            serializer = GeoServerSerialization(
                data=serializer_data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            serializer_data = {}

    @classmethod
    def get_info_db(cls):
        """METHOD for connect with database(geoserver-django) to create a geoserver layer
        """

        cnect_db = INPEGeoserverCopy.objects.get(pk=36)
        