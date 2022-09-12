from pool.models import Metadata


class DatastoreManager():

    @staticmethod
    def manager(workspaces, connection, db_info, geoserver_ip, instance):
        """MANAGER of Datastores
        ARGS:
            workspaces (list): All workspaces in DB and Geoserver
            connection (pool): An connection with geoserver to create, delete or reload
            db_info (dict): User and password from DB
            geoserver_ip (string): Geoserver url
            instance(instance): Info about Database
        Return:

        """

        status, workspace, datastore, pg_table = DatastoreManager.create_datastore(
            workspaces,
            connection,
            db_info,
            geoserver_ip,
            instance
        )
        return status, workspace, datastore, pg_table

    @classmethod
    def create_datastore(cls, workspaces, connection, db_info, username, instance):
        """METHOD to create Datastores, according with workspaces almost created and the postgis connection

        ARGS:
            workspaces (list): All workspaces in DB and Geoserver
            connection (pool): An connection with geoserver to create, delete or reload
            db_info (dict): User and password from DB
            geoserver_ip (string): Geoserver url
            instance(instance): Info about Database
        """

        schema_name = Metadata.objects.filter(
            geoserver_workspace__in=workspaces,
            geoserver_ip=username
        ).distinct('schema_name').values()

        for count in range(len( schema_name)):

            print('schemas to datastore: %s' %schema_name[count].get('schema_name'))
            print('dbinfo to connect (datastore): %s ' % db_info)

            store_name = instance.ip + '-'+ instance.port + '-' + instance.dbname + '-' + schema_name[count].get('schema_name')
            datastores = connection.create_featurestore(
                store_name=store_name,
                workspace= schema_name[count].get('geoserver_workspace'),
                db=instance.dbname,
                schema= schema_name[count].get('schema_name'),
                host='db',
                pg_user=db_info['name'],
                pg_password=db_info['password'],
            )
            print('Create DataStore: ', datastores)

            workspaces_by_ip = Metadata.objects.filter(
                geoserver_workspace= schema_name[count].get('geoserver_workspace'),
                geoserver_ip=username
            ).distinct('object_name').values()

            #LET'S PUBLISH LAYERS
            DatastoreManager.publish_feature_store(
                connection,
                schema_name[count].get('geoserver_workspace'),
                store_name,
                workspaces_by_ip 
            )

        return 'Done'

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

        print(publish)
        print(pg_query[count].get('object_name'))

