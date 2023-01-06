from django.test import TestCase
from geo.Geoserver import Geoserver
from pool.models import Metadata,Style,Workspaces


class TestConnectionPostGet(TestCase):

    def test_workspace_list(self):
        """Verificate if the connection_manager.py is saving on database the workspace's name
        """

        service_url = "https://geoserver-boavistarr.xskylab.com/geoserver/"
        values = {'name': 'erick.rocha', 'password': 'Erick1710#'}
        cnect_geo = Geoserver(
            service_url,
            username=values['name'],
            password=values['password'],
        )

        workspaces_list = []

        all_workspaces = cnect_geo.get_workspaces()

        if all_workspaces['workspaces']:
            if all_workspaces['workspaces']['workspace']:
                for value in range(len(all_workspaces['workspaces']['workspace'])):
                    workspaces_list.append(
                        all_workspaces['workspaces']['workspace'][value].get('name'))
        # print(workspaces_list)

        self.assertGreaterEqual(len(workspaces_list), 2)

        """Verificate if the connection_manager.py is saving on database the store's name
        """

        #service_url = "https://geoserver-boavistarr.xskylab.com/geoserver/"
        #values = {'name': 'XX', 'password': 'XX'}
        # cnect_geo = Geoserver(
        #    service_url,
        #    username=values['name'],
        #    password=values['password'],
        # )
#
        #datastore_list = []
#
#
        # for value in workspaces_list:
        #    datastore = cnect_geo.get_datastores(value)
        #    print(datastore)
        #    datastore_list.append(datastore['dataStores']['dataStore'][0]['name'])
        # print(datastore_list)

    def test_style_list(self):
        """Test to see the Workspaces on geoserver and verify if in database is registered, if not is necessary to create.
        """
        service_url = "https://geoserver-boavistarr.xskylab.com/geoserver/"
        values = {'name': 'erick.rocha', 'password': 'Erick1710#'}
        cnect_geo = Geoserver(
            service_url,
            username=values['name'],
            password=values['password'],
        )
        
        
        Metadata.objects.create(
            id=38, object_name='lim_lote_cad_a', schema_name='cadastro_urbano')
        Metadata.objects.create(id=39, object_name='lim_loteamento_a', schema_name='cadastro_urbano', geoserver_title='Loteamentos',
                                geoserver_style_uri='http://storage.googleapis.com/styles-xskylab-boavista-smart/STYLES/st_lim_loteamento_a.sld',
                                geoserver_workspace='CADASTRO_URBANO',
                                geoserver_ip='geoserver:8080/geoserver',
                                style_name = 'st_lim_loteamento_a')
        Workspaces.objects.create(
            geoserver_workspace ='CADASTRO_URBANO',
            geoserver_ip='geoserver:8080/geoserver'
        )
        workspaces = Workspaces.objects.filter(
            geoserver_workspace ='CADASTRO_URBANO',
            geoserver_ip='geoserver:8080/geoserver'
        ).distinct(
            'geoserver_workspace', 'geoserver_ip'
        ).values('geoserver_workspace', 'geoserver_ip')

        all_workspaces = cnect_geo.get_workspaces()
        all_workspaces_list = []
        for number_line in range(len(all_workspaces['workspaces']['workspace'])):
            all_workspaces_list.append(all_workspaces['workspaces']['workspace'][number_line].get('name'))
        print(all_workspaces_list)
        #print(all_workspaces['workspaces']['workspace']) 
        if str(workspaces[0]) in all_workspaces_list:
            print('%s alredy is on geoserver, skipping' %workspaces)
        else:
            print('Create on Geoserver')
        workspaces_dict = Metadata.objects.filter(
            geoserver_workspace="CADASTRO_URBANO"
        ).exclude(
            geoserver_style_uri='None'
        ).values(
            "id",
            "geoserver_workspace",
            "geoserver_style_uri",
            "style_name"
        )

        for workspace_name in workspaces_dict:

            instance = Workspaces.objects.get(geoserver_workspace=workspace_name.get('geoserver_workspace'))
            Style.objects.create(
                geoserver_workspace=instance,
                geoserver_style= workspace_name.get('geoserver_style_uri'),
                style_name=workspace_name.get('style_name')
            ).save()
            object=Style.objects.all().values()
            print(object[0])
        self.assertNotEquals(len(workspaces_dict),0)
