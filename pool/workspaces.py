from time import sleep
from geo.Geoserver import Geoserver
from .models import Workspaces, Metadata


class WorkspaceManager():
    cnect_geo = None
    filter_query = None

    @staticmethod
    def manager(cnect_geo, geoserver_ip):
        """MANAGER of workspaces
        ARGS:
            geoserver_ip (string): Geoserver's url
            cnect_geo () : pool with geoserver
        RETURNS:
            filter_query (query dict): Informations about distinct geoserver_ip and workspaces
        """

        # save created workspaces on db
        dict_response = WorkspaceManager.geoserver_list_workspaces(cnect_geo)

        WorkspaceManager.cnect_geo = cnect_geo

        objec = Metadata.objects.distinct(
            'geoserver_workspace').values('geoserver_workspace')

        # step to verificate if workspaces on db is equal to geoserver, if not
        # we're going to create
        WorkspaceManager.verificate_exists_workspaces(geoserver_ip)


        return WorkspaceManager.filter_query

    @classmethod
    def geoserver_list_workspaces(cls, param):
        """METHOD to get, and save in temp table,
        all workspaces registered on geoserver

        Args:
            param (dict): info about user and password connection with DB
        """

        response = param.get_workspaces()
        data = response
        print('Workspaces: %s' % data)

        # verification and save on temp table
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
    def verificate_exists_workspaces(cls, geoserver_ip):
        """METHOD to verificate if exists the workspace on geoserver
                IF exists in database will return the query in format of dictionary,
                if not, will return the divergent workspace. This is a problem!
        ARGS:
            geoserver_ip (string): Geoserver Url
        """
        all_workspaces = Metadata.objects.filter(geoserver_ip= geoserver_ip).distinct(
            'geoserver_workspace', 'geoserver_ip'
        ).values('geoserver_workspace', 'geoserver_ip')

        print(all_workspaces)
        list_result = []
        count = 0
        while True:
            try:
                subquery_to_list = all_workspaces[count]['geoserver_workspace']

                print("Workspaces on Metadata: %s\n" %
                      all_workspaces[count]['geoserver_workspace']
                )

                list_result.append(subquery_to_list)
                count += 1
            except Exception:
                break

        # It'll return the correspond data of DB in Geoserver,
        correspond_workspace = Workspaces.objects.filter(
            geoserver_workspace__in=list_result,
        ).distinct('geoserver_workspace').values('geoserver_workspace')

        print('HERE:',correspond_workspace)
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
    def workspaces_creator(cls, params):
        """METHOD to create workspaces inside DATABASE
        ARGS:
            params (list):Name of workspaces needs to create
        """

        for value_count in range(len(params)):
            WorkspaceManager.cnect_geo.create_workspace(
                workspace=params[value_count]
            )