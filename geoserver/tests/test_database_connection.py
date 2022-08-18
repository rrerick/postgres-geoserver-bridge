from django.test import TestCase
from geoserver.serializers import GeoServerSerialization
from geoserver.models import INPEGeoserverCopy

##Code your Tests here!

class TestDatabaseConnection(TestCase):

    def setUp(self):
        import psycopg2
        import os
        from psycopg2.extras import RealDictCursor

        self.cnect = psycopg2.connect(
            database=os.environ.get('dbname',),
            user=os.environ.get('user'),
            password=os.environ.get('password'),
            host=os.environ.get('host'),
            port=os.environ.get('port'),
        )

        self.curs = self.cnect.cursor(cursor_factory=RealDictCursor)
        self.curs.execute("SELECT metadata FROM _v_metadata_catalog")

        self.json_field = {}
        count = 0
        for record in self.curs:
            self.json_field[count] = dict(record)
            count += 1

    def test_Serialize_is_Ok(self):
        """TEST for confirm the seralization of Database
        """

        print(self.cnect)
        serializer_data = {}

        for count in range(len(self.json_field)):
            serializer_data['data'] = self.json_field[count]
            serializer = GeoServerSerialization(
                data=serializer_data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            serializer_data = {}

        obj = INPEGeoserverCopy.objects.count()

        self.assertNotEquals(obj, 0)

    def test_Get_Return_Information(self):
        """TEST for use the data into database to use in Geoserver
        """

        obj = INPEGeoserverCopy.objects.get(pk=1)
        print(obj)
