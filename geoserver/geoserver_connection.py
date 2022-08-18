"""
CONNECTION with geoserver
"""
from geo.Geoserver import Geoserver


class geoserver():
    cnect_geo = Geoserver(
        service_url='http://10.8.2.17:8080/geoserver',
        username='admin',
        password='geoserver'
    )

    @staticmethod
    def gerserver_workspace(workspace_name):
        """WORKSPACE creation, if not exists

        Args:
            workspace_name (query dict): workspace's name
        """
        geoserver.cnect_geo.create_workspace(workspace=workspace_name['INPE'])

    @classmethod
    def geoserver_db_cnect(cls, self):
        """USED for connecrion the Postgis with geoserver and publish this as a layer
                ** It is only useful for vector data
        Args:
            name (str): Workspace's name
            params (dict): Database Connection

        """
        geoserver.cnect_geo.create_featurestore(
            store_name='geo_data',
            workspace=self.name,
            db=self.params['db'],
            host=self.params['host'],
            schema=self.params['schema'],
            pg_user=self.params['user'],
            pg_password=self.params['password'],
        )

        geoserver.cnect_geo.publish_featurestore(
            store_name='geo_data',
            pg_table=self.params['table_name'],
            workspace=self.name
        )

