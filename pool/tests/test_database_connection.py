from operator import contains
from subprocess import list2cmdline
from urllib import response
from urllib.parse import quote_from_bytes
from xmlrpc.client import FastMarshaller
from django.test import TestCase
from pool.serializers import GeoServerSerialization
from pool.models import Metadata, Workspaces
import os
import psycopg2
from pool.connection_manager import all_connections
# Code your Tests here!


class TestDatabaseConnection(TestCase):

    def setUp(self):
        from psycopg2.extras import RealDictCursor

        """This connection going to be change, this will get info from JSON file.
        for connect wit many databases.
        """

        self.cnect = psycopg2.connect(
            database=os.environ.get('dbname',),
            user=os.environ.get('user'),
            password=os.environ.get('password'),
            host=os.environ.get('host'),
            port=os.environ.get('port'),
        )

        self.curs = self.cnect.cursor(cursor_factory=RealDictCursor)
        self.curs.execute(
            "SELECT metadata, object_name FROM _v_metadata_catalog")
        self.curs2 = self.cnect.cursor(cursor_factory=RealDictCursor)
        self.curs2.execute("SELECT object_name FROM _v_metadata_catalog")

        self.json_field = {}
        count = 0
        for record in self.curs:
            self.json_field[count] = dict(record)
            count += 1

    def test_connection_many_db(self):
        """Test to try connect with many databases, on the same port or host, or not
        """

        read_content1 = all_connections()

        validator = True
        while validator:
            try:
                read_content = next(read_content1)
                # print(read_content)
                connec = psycopg2.connect(
                    database=read_content.get('dbname',),
                    user=read_content.get('user'),
                    password=read_content.get('password'),
                    host=read_content.get('host'),
                    port=read_content.get('port'),
                )
                self.assertEquals(connec.info.transaction_status, 0)
            except StopIteration:
                validator = False

    def test_Serialize_is_Ok(self):
        """TEST for confirm the seralization of Database
        """
        from geo.Geoserver import Geoserver
        serializer_data = {}

        for count in range(len(self.json_field)):
            serializer_data['object_name'] = str(
                self.json_field[count]['object_name']
            )

            serializer_data['geoserver_title'] = str(
                self.json_field[count]['metadata'].get(
                    'geoserver_title'
                )
            )

            serializer_data['geoserver_style_uri'] = str(
                self.json_field[count]['metadata'].get(
                    'geoserver_style_uri'
                )
            )

            serializer_data['geoserver_workspace'] = str(
                self.json_field[count]['metadata'].get(
                    'geoserver_worskpace'
                )
            )

            serializer = GeoServerSerialization(
                data=serializer_data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer_data = {}

        obj = Metadata.objects.count()
        objec = Metadata.objects.all().values()

        query_dict = {}

        for i in objec:
            query_dict[i['id']] = dict(i)
            count += 1

        response_method = TestDatabaseConnection.verification_geoserver()
        if response_method:
            validate_existance = TestDatabaseConnection.verificate_exists(
                response_method, query_dict)

        else:
            cnect_geo = Geoserver(
                service_url='http://localhost:8080/geoserver',
                username=os.environ.get('USER_GEOSERVER'),
                password=os.environ.get('PASS_GEOSERVER')
            )
            cnect_geo.create_workspace(
                workspace=query_dict[1].get('geoserver_workspace'))

        self.assertNotEquals(obj, 0)

    @staticmethod
    def verification_geoserver():
        """Test to verificate if exists data in geoserver
        """
        import requests

        response = requests.get(
            'http://0.0.0.0:8080/geoserver/rest/workspaces.json',
            auth=(os.environ.get('USER_GEOSERVER'),
                  os.environ.get('PASS_GEOSERVER'))
        )

        data = response.json()

        if data['workspaces']:
            if data['workspaces']['workspace']:
                for count in range(len(data['workspaces']['workspace'])):
                    position = Workspaces.objects.create(
                        geoserver_workspace=data['workspaces']['workspace'][count].get(
                            'name')
                    )
                    position.save()
                return data['workspaces']['workspace']
            else:
                return None

    @staticmethod
    def verificate_exists(params, query_dict):
        """METHOD to verificate if exists the workspace on geoserver
        IF exists in database will return the query in format of dictionary,
        if not, will return the divergent workspace. This is a problem!

        Args:
            params (dict): response about all workspaces
        """
        from geo.Geoserver import Geoserver
        from django.db.models import Exists

        subquery = Metadata.objects.distinct(
            'geoserver_workspace'
        ).values('geoserver_workspace')

        list_result = ['Geoserver']

        subquery_to_str = str(subquery[0]['geoserver_workspace'])
        list_result.append(subquery_to_str)

        # It'll return the correspond data of DB in Geoserver,
        query = Workspaces.objects.filter(
            geoserver_workspace__in=list_result).values('geoserver_workspace')

        # It'll return the value that don't exists on Geoserver, but exists on DB
        query_to_return_diference = Metadata.objects.filter(
            ~Exists(query)
        ).values('geoserver_workspace').distinct()

        print(query_to_return_diference)
