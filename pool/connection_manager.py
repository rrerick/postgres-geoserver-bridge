"""
CONNECTION with database and get all metadata for creation purpose
"""
from user_profile.models import UsersGeoserver
from django.core.exceptions import ObjectDoesNotExist
import psycopg2
from django.utils.timezone import datetime
from pool.styles import StyleManager
from pool.workspaces import WorkspaceManager
from geo.Geoserver import Geoserver
from psycopg2.extras import RealDictCursor
from pool.serializers import GeoServerSerialization
from pool.models import Workspaces, Metadata
from pool.datastore import DatastoreManager
from psycopg2.errors import UndefinedTable
import jwt
import os


# MANAGER APP


class Geoserver_Db(object):
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
        connection = Geoserver_Db.manager_connections(
            db_info,
            instance
        )
        # query on database and serialize
        status_db = Geoserver_Db.pyscopg_query_on_db(connection)
        if ("TABLE DOESN'T EXISTS IN THIS DATABASE" == status_db):
            return status_db

        Geoserver_Db.serializing_result()

        # verificate the geoserver user
        connect_geoserver = Geoserver_Db.exists_user_ip()

        if connect_geoserver:
            for count in range(len(connect_geoserver)):

                # connect to geoserver
                cnect_geo, geoserver_ip, geoserver_auth = Geoserver_Db.geoserver_connection_param(
                    connect_geoserver,
                    count=count
                )

                # if connection is None raise an error, else begginnig to create
                if 'get_status error:' in str(Geoserver_Db.status):
                    error_raise = ' ERROR : Does Geoserver User is correctly?'
                    return error_raise
                else:

                    # MANAGER OF WORKSPACES, RETURN A QUERY WITH WORKSPACES IN COMMON WITH DB
                    WorkspaceManager.manager(
                        cnect_geo,
                        geoserver_ip
                    )
                    correspond_workspace = Geoserver_Db.generate_workspace_list(
                        cnect_geo)

                    print("WORKSPACES CREATED: %s" % correspond_workspace)
                    if correspond_workspace:
                        # MANAGER OF DATASTORE
                        DatastoreManager.manager(
                            correspond_workspace,
                            cnect_geo,
                            db_info,
                            geoserver_ip,
                            instance,
                            geoserver_auth
                        )

                        # MANAGER OF STYLES
                        StyleManager.manager(
                            geoserver_ip=geoserver_ip,
                            connection_geoserver=cnect_geo,
                            geoserver_params=geoserver_auth
                        )

            # Geoserver_Db.clear_workspaces.delete()

        # Geoserver_Db.clear_matadata.delete()
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
            Geoserver_Db.status(string): Geoserver's connection status
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

        Geoserver_Db.status = cnect_geo.get_status()
        print('Verify if geoserver can be connected')
        print( cnect_geo.get_workspaces())
        print(Geoserver_Db.status)
        if 'get_status error:' in Geoserver_Db.status:
            print('Can Not Connect with Geoserver, verify URL, PASSWORD')
        return cnect_geo, param[count]['geoserver_ip'], values

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
        try:
            curs = database_connection.cursor(cursor_factory=RealDictCursor)
            curs.execute(
                "SELECT metadata FROM public._v_metadata_catalog"
            )
            count = 0
            for record in curs:
                print(record)
                Geoserver_Db.json_field[count] = dict(record)
                count += 1
                print(record)
            curs.close()
        except UndefinedTable:
            return "TABLE DOESN'T EXISTS IN THIS DATABASE"
        except Exception as e:
            print(e)

    @classmethod
    def serializing_result(cls):
        """Serialize the result of query, when needs return the results turns easy
        """
        serializer_data = {}
        inner_count = 0
        for count in range(len(Geoserver_Db.json_field)):

            validator = True
            while validator:
                try:
                    serializer_data['schema_name'] = str(
                        Geoserver_Db.json_field[count]['metadata']['schema_name']
                    )

                    serializer_data['object_name'] = str(
                        Geoserver_Db.json_field[count]['metadata']['relation_name']
                    )
                    serializer_data['geoserver_title'] = str(
                        Geoserver_Db.json_field[count]['metadata']["geoserver"][inner_count].get(
                            "geoserver_layer_title"
                        )
                    )
                    serializer_data['geoserver_style_uri'] = str(
                        Geoserver_Db.json_field[count]['metadata']["geoserver"][inner_count].get(
                            'geoserver_style_uri'
                        )
                    )
                    serializer_data['geoserver_ip'] = str(
                        Geoserver_Db.json_field[count]['metadata']["geoserver"][inner_count].get(
                            "geoserver_instance_name"
                        )
                    )
                    serializer_data['geoserver_workspace'] = str(
                        Geoserver_Db.json_field[count]['metadata']["geoserver"][inner_count].get(
                            'geoserver_workspace'
                        )
                    )
                    serializer_data['style_name'] = str(
                        Geoserver_Db.json_field[count]['metadata']["geoserver"][inner_count].get(
                            'style_name'
                        )
                    )
                    print("%s :: We are serializing data \n %s" %(datetime.now(),serializer_data))
                    if serializer_data.get("schema_name") == 'public':
                        inner_count += 1
                        continue
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
            verify = Metadata.objects.distinct(
                'geoserver_style_uri').values('geoserver_style_uri')
            instance = Metadata.objects.exclude(geoserver_ip='None').values_list(
                'geoserver_ip').distinct('geoserver_ip')
            print('verificador: %s\n' % str(verify))
            print('\nGEOSERVER USERS ON METADATA: %s\n' % instance)
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

    @staticmethod
    def generate_workspace_list(connection_geoserver):
        """Method to create a list of existing workspaces
        ARGS:
            connection_geoserver (object): The connection with geoserver
        Return:
            workspaces_list (list): the names of workspaces in geoserver
        """
        print('generate workspace list . . . ')
        workspaces_list = []
        try:
            all_workspaces = connection_geoserver.get_workspaces()
            if all_workspaces['workspaces']:
                if all_workspaces['workspaces']['workspace']:
                    print(all_workspaces['workspaces'])
                    for value in range(len(all_workspaces['workspaces']['workspace'])):
                        workspaces_list.append(
                            all_workspaces['workspaces']['workspace'][value].get('name'))
        except Exception:
            print('0 workspaces registered')
        finally:
            return workspaces_list

    @staticmethod
    def generate_store_list(connection_geoserver):
        """Method to create a list of existing workspaces

        Args:
            connection_geoserver (object): Object to connect with geoserver
        """

        workspaces_list = Geoserver_Db.generate_workspace_list(
            connection_geoserver)

        datastore_list = []
        for value in workspaces_list:
            datastore = connection_geoserver.get_datastores(value)
            if datastore['dataStores']:
                if datastore['dataStores']['dataStore']:
                    datastore_list.append(
                        datastore['dataStores']['dataStore'][0]['name'])


        return datastore_list,workspaces_list