from pool.models import Metadata, Store
from pool.models import Workspaces
from pool.workspaces import WorkspaceManager
import pool.connection_manager as cm
import requests
import json


class DatastoreManager():

    @staticmethod
    def manager(workspaces, connection, db_info, geoserver_ip, instance, geoserver_auth):
        """MANAGER of Datastores
        ARGS:
            workspaces (list): All workspaces in DB and Geoserver
            connection (pool): An connection with geoserver to create, delete or reload
            db_info (dict): User and password from DB
            geoserver_ip (string): Geoserver url
            instance(instance): Info about Database
            geoserver_auth (dict): User and password of geoserver
        Return:

        """

        DatastoreManager.geoserver_list_stores(connection)

        status, workspace, datastore, pg_table = DatastoreManager.create_datastore(
            workspaces,
            connection,
            db_info,
            geoserver_ip,
            instance,
            geoserver_auth
        )
        return status, workspace, datastore, pg_table

    @classmethod
    def geoserver_list_stores(cls, param):
        """METHOD to get, and save in temp table,
        all workspaces registered on geoserver

        Args:
            param (dict): info about user and password connection with DB
        """

        data, workspace_list = cm.Geoserver_Db.generate_store_list(param)

        for count in range(len(data)):
            object_to_save, resp = Store.objects.filter(
                geoserver_workspace=Workspaces.objects.filter(
                    geoserver_workspace=workspace_list[count]).values('id')[0]['id'],
                geoserver_store=data[count]
            ).get_or_create(
                geoserver_workspace=Workspaces.objects.get(
                    geoserver_workspace=workspace_list[count]),
                geoserver_store=data[count])
            if resp is False:
                object_to_save.save()

        return data

    @classmethod
    def verificate_exists_workspaces(cls, geoserver_ip):
        """METHOD to verificate if exists the workspace on geoserver
                IF exists in database will return the query in format of dictionary,
                if not, will return the divergent workspace. This is a problem!
        ARGS:
            geoserver_ip (string): Geoserver Url
        """
        all_datastores = Metadata.objects.filter(geoserver_ip=geoserver_ip).distinct(
            'geoserver_workspace', 'geoserver_ip'
        ).values('geoserver_workspace', 'geoserver_ip')

        list_result = []
        count = 0
        while True:
            try:
                subquery_to_list = all_datastores[count]['geoserver_workspace']

                print("Workspaces on Metadata: %s\n" %
                      all_datastores[count]['geoserver_workspace']
                      )

                list_result.append(subquery_to_list)
                count += 1
            except Exception:
                break

        # It'll return the correspond data of DB in Geoserver,
        correspond_workspace = Workspaces.objects.filter(
            geoserver_workspace__in=list_result,
        ).distinct('geoserver_workspace').values('geoserver_workspace')

        print('HERE:', correspond_workspace)
        # this query it's important because has all workspaces equal to DB
        WorkspaceManager.filter_query = correspond_workspace
        print("Equals to DB: %s\n" % correspond_workspace)

        # It'll return the value that don't exists on Geoserver, but exists on DB
        query_to_return_difference = Metadata.objects.exclude(
            geoserver_workspace__in=correspond_workspace
        ).filter(geoserver_ip=geoserver_ip).values('geoserver_workspace')
        print("Needs to Create: %s\n" % query_to_return_difference)

        needs_to_create_list = []

        for value_count in range(len(query_to_return_difference)):
            query_to_list = query_to_return_difference[value_count]['geoserver_workspace']
            needs_to_create_list.append(query_to_list)
        print('needs to create list', needs_to_create_list)
        # create what's needs to
        return WorkspaceManager.workspaces_creator(needs_to_create_list)

    @classmethod
    def create_datastore(cls, workspaces, connection, db_info, username, instance, geoserver_auth):
        """METHOD to create Datastores, according with workspaces almost created and the postgis connection

        ARGS:
            workspaces (list): All workspaces in DB and Geoserver
            connection (pool): An connection with geoserver to create, delete or reload
            db_info (dict): User and password from DB
            geoserver_ip (string): Geoserver url
            instance(instance): Info about Database
            geoserver_auth (dict): User and password of geoserver
        """

        schema_name = Metadata.objects.filter(
            geoserver_workspace__in=workspaces,
            geoserver_ip=username
        ).distinct('geoserver_workspace').values()

        print(schema_name, '\n')
        for count in range(len(schema_name)):
            print(count)
            print('workspace to datastore: %s' %
                  schema_name[count].get('geoserver_workspace'))
            store_name = schema_name[count].get('geoserver_workspace')

            try:
                # Validate Before create, if exists continue, else create and publish
                validate_store = Store.objects.filter(geoserver_workspace=Workspaces.objects.filter(
                    geoserver_workspace=schema_name[count].get('geoserver_workspace')).values('id')[0]['id']).values_list()
                print(validate_store)
                validate_store[0]
                print('Store(s) %s alredy exists \nSKIPPING' % validate_store)
            except IndexError:
                datastores = connection.create_featurestore(
                    store_name=store_name,
                    workspace=schema_name[count].get('geoserver_workspace'),
                    db=instance.dbname,
                    schema=schema_name[count].get('schema_name'),
                    host=instance.ip,
                    pg_user=db_info['name'],
                    pg_password=db_info['password'],
                )
                print('\nCreate DataStore: %s on workspace %s' %
                      (datastores, schema_name[count].get('schema_name')))

                workspaces_by_ip = Metadata.objects.filter(
                    geoserver_workspace=schema_name[count].get(
                        'geoserver_workspace'),
                    geoserver_ip=username
                ).distinct('object_name').values()

                # LET'S PUBLISH LAYERS
                DatastoreManager.publish_feature_store(
                    connection,
                    schema_name[count].get('geoserver_workspace'),
                    store_name,
                    workspaces_by_ip,
                    geoserver_auth,
                    username
                )
            finally:
                return 'Done'

    @classmethod
    def publish_feature_store(cls, connection, workspace_name, store_name, pg_query, geoserver_auth, geoserver_ip):

        for count in range(len(pg_query)):
            try:
                print('\nPublish Table: %s' %
                      pg_query[count].get('object_name'))
                publish = connection.publish_featurestore(
                    workspace=workspace_name,
                    store_name=store_name,
                    pg_table=pg_query[count].get('object_name'),
                )

                if 'Create DataStore: 500:' in publish:
                    print(publish)
                    continue
                else:
                    # alter title and other things
                    DatastoreManager.post_layer_informations(
                        workspace_name=workspace_name,
                        datastore_name=store_name,
                        layer_name=pg_query[count],
                        geoserver_auth=geoserver_auth,
                        ip=geoserver_ip
                    )
            except Exception as e:
                print('ERROR: %s' % e)

    @classmethod
    def post_layer_informations(cls, ip: str, workspace_name: str, datastore_name: str, layer_name: dict, geoserver_auth: dict):
        """METHOD to change layer title, layer numDecimals and layer forcedDecimal to true
        ARGS:
            ip (string): Geoserver url
            workspace_name (str)
            datastore_name (str)
            layer_name (str)
            geoserver_auth (dict): User and password of geoserver
        """

        title = layer_name.get('geoserver_title')
        if title == 'None':
            print("Title with 'null' value, use the same name of table")
            title = layer_name.get('object_name')

        session = requests.Session()
        data = {"featureType": {"title": title,
                                "numDecimals": "15", "forcedDecimal": True, }}
        data = json.dumps(data)

        url_name = 'https://%s/rest/workspaces/%s/datastores/%s/featuretypes/%s.json' % (
            ip, workspace_name, datastore_name, layer_name.get('object_name'))

        print(url_name)

        auth_tuple = (geoserver_auth['name'], geoserver_auth['password'])

        status = session.put(
            url=url_name,
            data=data,
            auth=auth_tuple,
            headers={"Accept": "application/json",
                     "content-type": "application/json"},
        )
        print('status alteration layer: %s' % status)
        session.close()
