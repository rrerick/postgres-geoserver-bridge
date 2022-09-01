"""
CONNECTION with database and get all metadata for creation purpose

Explain ideias:
    Connection with Database
    View the metadata field
    get information
    Separate Geoserver info


"""

import psycopg2
from user_profile.models import Db_info, Pg_User
from geoserver.workspaces import WorkspaceManager
from geo.Geoserver import Geoserver
from psycopg2.extras import RealDictCursor
from .serializers import GeoServerSerialization
from .models import Workspaces, Metadados
from geoserver.datastore import DatastoreManager

#MANAGER APP

class GEOSERVER_DB():
    json_field = {}
    clear_data = Workspaces.objects.all()
    clear_principal_data = Metadados.objects.all()
    cnect_geo = None

    @staticmethod
    def manager_db_with_geoserver(param, user_info, db_info, decrypted_password):
        """Master of GEOSERVER and Database
        Args:
            param (dict): info about GEOSERVER'S user
            user_info (instance): info about  Postgres user
            db_info (instance) : info about Database to connect
            decrypted_passweord : password of database user
        """

        #connect to geoserver
        cnect_geo, actual_generator = GEOSERVER_DB.geoserver_connection_param(param)
        GEOSERVER_DB.cnect_geo = cnect_geo

        #connect with database
        connection = GEOSERVER_DB.manager_connections(user_info, db_info, decrypted_password)

        #query on database
        GEOSERVER_DB.pyscopg_query_on_db(connection)
        GEOSERVER_DB.serializing_result()

        #MANAGER OF WORKSPACES, RETURN A QUERY WITH WORKSPACES IN COMMON WITH DB
        query = WorkspaceManager.manager(actual_generator, cnect_geo)

        #MANAGER OF DATASTORE
        DatastoreManager.manager(query, cnect_geo, user_info, db_info, decrypted_password)
        GEOSERVER_DB.clear_data.delete()
        GEOSERVER_DB.clear_principal_data.delete()

        return 'Done!'
    @classmethod
    def geoserver_connection_param(cls, param):
        """Connect with Geoserver
        Args:
            param (dict) : geoserver's user
        Return
            cnect_geo (yield - instance): Connection's instance
            actual_instace (generator -next ): if has more than one geoserver's user
        """

        params=param
        cnect_geo = Geoserver(
            service_url=params.get('ip'),
            username=params.get('username'),
            password=params.get('password').decode(),
        )
        actual_generator = params
        return cnect_geo,actual_generator



    @classmethod
    def manager_connections(cls,user_info, db_info, decrypted_password):
        """Method to connect with database
        Return:
            connec (): poll of connection
        """

        connec = psycopg2.connect(
            database=db_info.dbname,
            user=user_info.username,
            password=decrypted_password,
            host=db_info.ip,
            port=db_info.port,
        )

        return connec

    @classmethod
    def pyscopg_query_on_db(cls, database_connection):
        """METHOD to select metadata , object_name and schema_name on database.
        Args:
           params : connection with db
        RETURN:
            json_field (json): colected informations
        """
        curs = database_connection.cursor(cursor_factory=RealDictCursor)
        curs.execute(
            "SELECT metadata, object_name,schema_name FROM _v_metadata_catalog"
        )

        count = 0
        for record in curs:
            GEOSERVER_DB.json_field[count] = dict(record)
            count += 1

        curs.close()

    @classmethod
    def serializing_result(cls):
        """Serialize the result of query, when needs return the results turns easy
        """
        serializer_data = {}

        for count in range(len(GEOSERVER_DB.json_field)):

            serializer_data['schema_name'] = str(
                GEOSERVER_DB.json_field[count]['schema_name']
            )
            print(GEOSERVER_DB.json_field[count]['schema_name'])
            serializer_data['object_name'] = str(
                GEOSERVER_DB.json_field[count]['object_name']
            )
            print(GEOSERVER_DB.json_field[count]['object_name'])
            serializer_data['geoserver_title'] = str(
                GEOSERVER_DB.json_field[count]['metadata'].get(
                    'geoserver_title'
                )
            )
            serializer_data['geoserver_style_uri'] = str(
                GEOSERVER_DB.json_field[count]['metadata'].get(
                    'geoserver_style_uri'
                )
            )
            serializer_data['geoserver_workspace'] = str(
                GEOSERVER_DB.json_field[count]['metadata'].get(
                    'geoserver_worskpace'
                )
            )
            serializer = GeoServerSerialization(
                data=serializer_data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer_data = {}
