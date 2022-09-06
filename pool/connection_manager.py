"""
CONNECTION with database and get all metadata for creation purpose

Explain ideias:
    Connection with Database
    View the metadata field
    get information
    Separate Geoserver info


"""
from django.core.exceptions import ObjectDoesNotExist
import psycopg2
from pool.workspaces import WorkspaceManager
from geo.Geoserver import Geoserver
from psycopg2.extras import RealDictCursor
from .serializers import GeoServerSerialization
from .models import Workspaces, Metadata
from pool.datastore import DatastoreManager
from user_profile.models import Token
from cryptography.fernet import Fernet

# MANAGER APP


class GEOSERVER_DB():
    json_field = {}
    clear_workspaces = Workspaces.objects.all()
    clear_matadata = Metadata.objects.all()
    status = None

    @staticmethod
    def manager_db_with_geoserver(db_info, decrypted_password):
        """Master of GEOSERVER and Database
        Args:
            db_info (instance) : info about Database to connect
            decrypted_passweord : password of database user
        """
        # connect with database
        connection = GEOSERVER_DB.manager_connections(
            db_info, decrypted_password)

        # query on database and serialize
        GEOSERVER_DB.pyscopg_query_on_db(connection)
        GEOSERVER_DB.serializing_result()

        # verificate the geoserver user
        connect_geoserver = GEOSERVER_DB.exists_user_ip(db_info)

        if connect_geoserver:
            for count in range(len(connect_geoserver)):
                # connect to geoserver
                cnect_geo, username = GEOSERVER_DB.geoserver_connection_param(
                    connect_geoserver, count=count)

                #if connection is None raise an error, else begginnig to create
                print(GEOSERVER_DB.status)
                if 'get_status error:' in str(GEOSERVER_DB.status):
                    error_raise = ' ERROR : Does Geoserver User is correctly?'
                    return error_raise
                else:
                    # MANAGER OF WORKSPACES, RETURN A QUERY WITH WORKSPACES IN COMMON WITH DB
                    query = WorkspaceManager.manager(
                        cnect_geo, username
                    )
                    """Create Datastores:
                    The logical is commenteded, before it's needs to change the metadata to an official one.
                    """
                    if query:
                        # MANAGER OF DATASTORE
                        status, workspace, datastore, pg_table, = DatastoreManager.manager(
                            query, cnect_geo, db_info, decrypted_password,username)
                        #if status:
                        #    return '%s (%s:%s) %s' %(status, workspace, datastore, pg_table)
                    else:
                        continue

                GEOSERVER_DB.clear_workspaces.delete()
        GEOSERVER_DB.clear_matadata.delete()
        return 'Done'

    @classmethod
    def geoserver_connection_param(cls, param, count):
        """Connect with Geoserver
        Args:
            param (instance) : geoserver's user
            count (int): number of 'for' loop
        Return
            cnect_geo (): Connection's instance
            username (string): Name of User on geoserver
            GEOSERVER_DB.status(string): Geoserver's connection status
        """

        params = param

        f = Fernet(params[count].get('pub_key'))
        password = f.decrypt(params[count].get('token').encode())
        password = password.decode()  # tuple

        username = params[count].get('user')
        service_url = params[count].get('ip')  # take off tuple

        cnect_geo = Geoserver(
            service_url,
            username=username,
            password=password,
        )

        GEOSERVER_DB.status = cnect_geo.get_status()

        return cnect_geo, username

    @classmethod
    def manager_connections(cls, db_info, decrypted_password):
        """Method to connect with database
        Return:
            connec (): poll of connection
        """

        connec = psycopg2.connect(
            database=db_info.dbname,
            user=db_info.username,
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

            serializer_data['object_name'] = str(
                GEOSERVER_DB.json_field[count]['object_name']
            )
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
            serializer_data['geoserver_ip'] = str(
                GEOSERVER_DB.json_field[count]['metadata'].get(
                    'geoserver_ip'
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
            print('%s: Serialized!' % (serializer_data['schema_name']))
            serializer_data = {}

    @classmethod
    def exists_user_ip(cls, db_info):
        """METHOD to verificate if exists a geoserver
        users registered with the same ip as Metadata table
        RETURNS:
            result(query_dict): With informations about the Geoserver Users
        """

        count = 1
        validator = True
        while validator:
            instance = Metadata.objects.values_list('geoserver_ip')
            print('GEOSERVER USERS ON METADATA: %s' % instance)
            if instance:
                count += 1
                try:
                    result = Token.objects.filter(user__in=instance).values()
                    print('Registered Users: %s\n' % result)
                    return result
                except ObjectDoesNotExist:
                    result = None
                    break
            else:
                validator = False
