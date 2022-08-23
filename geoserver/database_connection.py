"""
CONNECTION with database and get all metadata for creation purpose

Explain ideias:
    Connection with Database
    View the metadata field
    get information
    Separate Geoserver info


"""
import os
import psycopg2
import json
import requests
from geo.Geoserver import Geoserver
from psycopg2.extras import RealDictCursor
from .serializers import GeoServerSerialization
from .models import Workspaces, INPEGeoserverCopy
from django.db.models import Exists, CharField, BooleanField, OuterRef
from django.db.models.functions import Cast,Coalesce


class GEOSERVER_DB():
    json_field = {}
    clear_data = Workspaces.objects.all()
    clear_principal_data = INPEGeoserverCopy.objects.all()
    cnect_geo = Geoserver(
        service_url='http://localhost:8080/geoserver',
        username=os.environ.get('USER_GEOSERVER'),
        password=os.environ.get('PASS_GEOSERVER')
    )

    @staticmethod
    def manager_db_with_geoserver():
        """Master of GEOSERVER and Database
        """

        connection = GEOSERVER_DB.manager_connections()

        GEOSERVER_DB.pyscopg_query_on_db(next(connection))
        GEOSERVER_DB.serializing_result()
        dict_response = GEOSERVER_DB.geoserver_list_workspaces()

        objec = INPEGeoserverCopy.objects.distinct(
            'geoserver_workspace').values('geoserver_workspace')


        if dict_response:
            GEOSERVER_DB.verificate_exists_workspaces()

        else:
            for value in range(len(objec)):
                GEOSERVER_DB.cnect_geo.create_workspace(
                    workspace=objec[value]['geoserver_workspace']
                )

        GEOSERVER_DB.clear_data.delete()
        GEOSERVER_DB.clear_principal_data.delete()

    @classmethod
    def manager_connections(cls):
        """Master of CONNECTION on databases
        Return:
            An iteration with the connection
        """
        read_content1 = all_connections()

        validator = True
        while validator:
            try:
                read_content = next(read_content1)

                connec = psycopg2.connect(
                    database=read_content.get('dbname',),
                    user=read_content.get('user'),
                    password=read_content.get('password'),
                    host=read_content.get('host'),
                    port=read_content.get('port'),
                )
                yield connec
            except StopIteration:
                validator = False

    @classmethod
    def pyscopg_query_on_db(cls, params):
        """METHOD to select metadata and object_name on database.
        Args:
            params : connection with db
        """
        curs = params.cursor(cursor_factory=RealDictCursor)
        curs.execute(
            "SELECT metadata, object_name FROM _v_metadata_catalog"
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
            serializer_data['object_name'] = str(
                GEOSERVER_DB.json_field[count]['object_name'])
            serializer_data['geoserver_title'] = str(GEOSERVER_DB.json_field[count]['metadata'].get(
                'geoserver_title'
            ))
            serializer_data['geoserver_style_uri'] = str(GEOSERVER_DB.json_field[count]['metadata'].get(
                'geoserver_style_uri'
            ))
            serializer_data['geoserver_workspace'] = str(GEOSERVER_DB.json_field[count]['metadata'].get(
                'geoserver_worskpace'
            ))
            serializer = GeoServerSerialization(
                data=serializer_data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer_data = {}

    @classmethod
    def geoserver_list_workspaces(cls):
        """METHOD to bring, and save in temp db, all workspaces registered on geoserver
        """

        response = requests.get(
            'http://0.0.0.0:8080/geoserver/rest/workspaces.json',
            auth=(os.environ.get('USER_GEOSERVER'),
                  os.environ.get('PASS_GEOSERVER'))
        )

        data = response.json()

        if data['workspaces']:
            if data['workspaces']['workspace']:
                for count in range(len(data['workspaces']['workspace'])):
                    object_to_save = Workspaces.objects.create(
                        geoserver_workspace=data['workspaces']['workspace'][count].get(
                            'name')
                    )
                    object_to_save.save()
                return data['workspaces']['workspace']
            else:
                return None

    @classmethod
    def verificate_exists_workspaces(cls):
        """METHOD to verificate if exists the workspace on geoserver
        IF exists in database will return the query in format of dictionary,
        if not, will return the divergent workspace. This is a problem!

        Args:
            params (dict): response about all workspaces
        """

        subquery = INPEGeoserverCopy.objects.distinct(
            'geoserver_workspace'
        ).values('geoserver_workspace')
        

        list_result = []
        list_query_result = []
        count = 0
        while True:
            try:
                subquery_to_list = str(subquery[count]['geoserver_workspace'])
                print(subquery[count]['geoserver_workspace'])
                list_result.append(subquery_to_list)
                count += 1

            except Exception:
                break

        print(list_result)
        # It'll return the correspond data of DB in Geoserver,
        query = Workspaces.objects.filter(
            geoserver_workspace__in = list_result,
        ).distinct().values('geoserver_workspace')


        print("Equals to DB: ", query)
        # It'll return the value that don't exists on Geoserver, but exists on DB
        query_to_return_difference = INPEGeoserverCopy.objects.exclude(
            geoserver_workspace__in=query
        ).values('geoserver_workspace')
        print("Needs to Create : ", query_to_return_difference)

        needs_to_create_list = []

        for value_count in range(len(query_to_return_difference)):
            query_to_list = query_to_return_difference[value_count]['geoserver_workspace']
            needs_to_create_list.append(query_to_list)

        return GEOSERVER_DB.workspaces_creator(needs_to_create_list)

    @classmethod
    def workspaces_creator(cls, params):
        """METHOD to create workspaces inside DATABASE
        ARGS:
            params (list):Name of workspaces needs to create
        """

        for value_count in range(len(params)):
            GEOSERVER_DB.cnect_geo.create_workspace(
                workspace=params[value_count]
            )


def all_connections():
    """Return all connections possibles
    Return
        yield
    """

    current_dir = os.getcwd() + '/geoserver/ips_databases.json'
    read_content1 = json.load(open(current_dir, "r"))
    for count in range(len(read_content1)):
        count = str(count)
        yield dict(read_content1[count])
