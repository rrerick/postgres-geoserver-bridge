"""
Cria e gerencia datastores
1. Tabela banco -- Datastore e schema relacionado
"""

from geo.Geoserver import Geoserver
from geoserver.models import Metadados,Workspaces

class DatastoreManager():

    @staticmethod
    def manager(query,connection,user_info, db_info, decrypted_password):

        DatastoreManager.create_datastore(query ,connection,user_info, db_info, decrypted_password)

    @classmethod
    def create_datastore(cls,query, connection,user_info, db_info, decrypted_password ):
        workspaces = connection.get_workspaces()
        query2 = Metadados.objects.filter(
            geoserver_workspace__in=query
        ).distinct('schema_name').values()


        for count in range(len(query2)):

            connection.create_featurestore(
                store_name='geodata%i' %(count),
                workspace=query2[count].get('geoserver_workspace'),
                db = db_info.dbname,
                schema = query2[count].get('schema_name'),
                host = db_info.ip, 
                pg_user = user_info.username,
                pg_password = decrypted_password
            )

