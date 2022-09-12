"""
CONNECTION with database and get all metadata for creation purpose

Explain ideias:
    Connection with Database
    View the metadata field
    get information
    Separate Geoserver info


"""
from user_profile.models import UsersGeoserver
from django.core.exceptions import ObjectDoesNotExist
import psycopg2
from pool.workspaces import WorkspaceManager
from geo.Geoserver import Geoserver
from psycopg2.extras import RealDictCursor
from .serializers import GeoServerSerialization
from .models import Workspaces, Metadata
from pool.datastore import DatastoreManager
import jwt,os


# MANAGER APP


class GEOSERVER_DB():
    json_field = {}
    clear_workspaces = Workspaces.objects.all()
    clear_matadata = Metadata.objects.all()
    status = None

    @staticmethod
    def manager_db_with_geoserver(db_info, instance):
        """Master of GEOSERVER and Database
        Args:
            db_info (instance) : info about Database to connect
            decrypted_passweord : password of database user
        """
        # connect with database
        connection = GEOSERVER_DB.manager_connections(
            db_info,
            instance
        )

        # query on database and serialize
        GEOSERVER_DB.pyscopg_query_on_db(connection)
        GEOSERVER_DB.serializing_result()

        # verificate the geoserver user
        connect_geoserver = GEOSERVER_DB.exists_user_ip()

        if connect_geoserver:
            for count in range(len(connect_geoserver)):

                # connect to geoserver
                cnect_geo, geoserver_ip = GEOSERVER_DB.geoserver_connection_param(
                    connect_geoserver,
                    count=count
                )

                # if connection is None raise an error, else begginnig to create
                if 'get_status error:' in str(GEOSERVER_DB.status):
                    error_raise = ' ERROR : Does Geoserver User is correctly?'
                    return error_raise
                else:
                    # MANAGER OF WORKSPACES, RETURN A QUERY WITH WORKSPACES IN COMMON WITH DB
                    correspond_workspace = WorkspaceManager.manager(
                        cnect_geo,
                        geoserver_ip
                    )
                    """Create Datastores:
                    The logical is commenteded, before it's needs to change the metadata to an official one.
                    """
                    if correspond_workspace:
                        # MANAGER OF DATASTORE
                        status = DatastoreManager.manager(
                            correspond_workspace,
                            cnect_geo,
                            db_info,
                            geoserver_ip,
                            instance
                        )
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
            geoserver_ip (string): Name of User on geoserver
            GEOSERVER_DB.status(string): Geoserver's connection status
        """
        my_secret = os.getenv('secret')
        values = jwt.decode(
            param[count]['authtk'],
            key=my_secret,
            algorithms=['HS256']
        )

        service_url = 'http://' + param[count]['geoserver_ip']
        cnect_geo = Geoserver(
            service_url,
            username=values['name'],
            password=values['password'],
        )

        GEOSERVER_DB.status = cnect_geo.get_status()
        return cnect_geo, param[count]['geoserver_ip']

    @classmethod
    def manager_connections(cls, db_info, instance):
        """Method to connect with database
        Return:
            connec (): poll of connection
        """

        connec = psycopg2.connect(
            database=instance.dbname,
            user=db_info['name'],
            password=db_info['password'],
            host=instance.ip,
            port=instance.port,
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
            "SELECT metadata FROM _v_metadata_catalog"
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
        inner_count = 0
        for count in range(len(GEOSERVER_DB.json_field)):

            validator = True
            while validator:
                try:
                    serializer_data['schema_name'] = str(
                        GEOSERVER_DB.json_field[count]['metadata']['schema_name']
                    )

                    serializer_data['object_name'] = str(
                        GEOSERVER_DB.json_field[count]['metadata']['relation_name']
                    )
                    serializer_data['geoserver_title'] = str(
                        GEOSERVER_DB.json_field[count]['metadata']["geoserver"][inner_count].get(
                            "geoserver_layer_title"
                        )
                    )
                    serializer_data['geoserver_style_uri'] = str(
                        GEOSERVER_DB.json_field[count]['metadata']["geoserver"][inner_count].get(
                            'geoserver_style_uri'
                        )
                    )
                    serializer_data['geoserver_ip'] = str(
                        GEOSERVER_DB.json_field[count]['metadata']["geoserver"][inner_count].get(
                            "geoserver_instance_name"
                        )
                    )
                    serializer_data['geoserver_workspace'] = str(
                        GEOSERVER_DB.json_field[count]['metadata']["geoserver"][inner_count].get(
                            'geoserver_workspace'
                        )
                    )

                    serializer = GeoServerSerialization(
                        data=serializer_data
                    )
                    inner_count += 1
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    print('%s: Serialized!' % (serializer_data['schema_name']))
                    serializer_data = {}
                except IndexError:
                    inner_count = 0
                    validator = False

    @classmethod
    def exists_user_ip(cls):
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
                    result = UsersGeoserver.objects.filter(
                        geoserver_ip__in=instance).values()
                    print('Registered Users: %s\n' % result)
                    return result
                except ObjectDoesNotExist:
                    result = None
                    break
            else:
                validator = False
