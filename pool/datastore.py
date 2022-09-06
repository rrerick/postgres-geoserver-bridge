"""
Cria e gerencia datastores
1. Tabela banco -- Datastore e schema relacionado
"""

from geo.Geoserver import Geoserver
from pool.models import Metadata, Workspaces
from pool.workspaces import WorkspaceManager


class DatastoreManager():

    @staticmethod
    def manager(query, connection, db_info, decrypted_password, username):

        status, workspace, datastore, pg_table = DatastoreManager.create_datastore(
            query, connection, db_info, decrypted_password, username)
        return status, workspace, datastore, pg_table
    @classmethod
    def create_datastore(cls, query, connection, db_info, decrypted_password, username):

        query2 = Metadata.objects.filter(
            geoserver_workspace__in=query,
            geoserver_ip=username
        ).distinct('schema_name').values()

        for count in range(len(query2)):

            print('schemas to datastore: %s' %
                  query2[count].get('schema_name'))
            print('dbinfo to connect (datastore): %s ' % db_info)

            datastores = connection.create_featurestore(
                store_name='geodata%i' % (count),
                workspace=query2[count].get('geoserver_workspace'),
                db=db_info.dbname,
                schema=query2[count].get('schema_name'),
                host='db',
                pg_user=db_info.username,
                pg_password=decrypted_password
            )
            print('Create DataStore: ', datastores)

            query3 = Metadata.objects.filter(
                geoserver_workspace=query2[count].get('geoserver_workspace'),
                geoserver_ip=username
            ).distinct('object_name').values()


            status,workspace, datastore, pg_table =  DatastoreManager.publish_feature_store(
                connection,
                query2[count].get('geoserver_workspace'),
                'geodata%i' % (count),
                query3
            )

            #if 'already exists' in status:
            #    continue
            #else:
            #    return status, workspace,datastore, pg_table
        status = 'Done'
        return status, None, None, None
    @staticmethod
    def publish_feature_store(connection, workspace_name, store_name, pg_query):
        
        print(pg_query, '\n\n')
        for count in range(len(pg_query)):
            publish = connection.publish_featurestore(
                workspace=workspace_name,
                store_name=store_name,
                pg_table=pg_query[count].get('object_name'),
            )

        print(publish)
        print(pg_query[count].get('object_name'))

        #if 'Data can not be published' in publish :
        #    return 'Data can not be published', workspace_name, store_name, pg_query[count].get('object_name') 
        #elif '400' in publish:
        #    return '400: Data can not be published!', workspace_name, store_name, pg_query[count].get('object_name')
        #else:
        return 'Done', None, None, None