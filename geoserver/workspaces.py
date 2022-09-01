"""
CLASSE PARA CRIAR E VERIFICAR WORKSPACES
"""
import requests
from geo.Geoserver import Geoserver
from .models import Workspaces, Metadados

class WorkspaceManager():
    cnect_geo = None
    filter_query = None
    @staticmethod
    def manager (actual_generator, cnect_geo):
        """MANAGER of workspaces
        ARGS:
            actual_generator (generator): About the actual generator
                of user and password at geoserver
            cnect_geo () : pool with geoserver
        """

        #save created workspaces on db
        dict_response = WorkspaceManager.geoserver_list_workspaces(cnect_geo)

        objec = Metadados.objects.distinct(
            'geoserver_workspace').values('geoserver_workspace')

        #step to verificate if workspaces on db is equal to geoserver, if not
        #we're going to create
        if dict_response:
            WorkspaceManager.verificate_exists_workspaces()

        else:
            for value in range(len(objec)):
                cnect_geo.create_workspace(
                    workspace=objec[value]['geoserver_workspace']
                )

        return WorkspaceManager.filter_query

    @classmethod
    def geoserver_list_workspaces(cls,param):
        """METHOD to get, and save in temp table,
        all workspaces registered on geoserver

        Args:
            param (dict): info about user and password connection with DB
        """

        response = param.get_workspaces()
        data = response

        #verification and save on temp table
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
        """
        subquery = Metadados.objects.distinct(
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

        # It'll return the correspond data of DB in Geoserver,
        query = Workspaces.objects.filter(
            geoserver_workspace__in=list_result,
        ).distinct().values('geoserver_workspace')
        
        #this query it's important because has all workspaces equal to DB
        WorkspaceManager.filter_query = query
        print("Equals to DB: ", query)

        # It'll return the value that don't exists on Geoserver, but exists on DB
        query_to_return_difference = Metadados.objects.exclude(
            geoserver_workspace__in=query
        ).values('geoserver_workspace')
        print("Needs to Create : ", query_to_return_difference)

        needs_to_create_list = []

        for value_count in range(len(query_to_return_difference)):
            query_to_list = query_to_return_difference[value_count]['geoserver_workspace']
            needs_to_create_list.append(query_to_list)

        #create what's needs to
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
