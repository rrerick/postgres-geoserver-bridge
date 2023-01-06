import os
import requests
from pool.models import Metadata,Style,Workspaces


class StyleManager(object):
    """Class to manager the add and delete of styles on geoserver
    """

    workpace_name = None
    style_name = None
    geoserver_style_name = None

    @staticmethod
    def manager(geoserver_ip, connection_geoserver, geoserver_params):

        route_file_generator = StyleManager.get_style_link(
            geoserver_ip=geoserver_ip)

        validator = True
        while validator:
            try:
                route_file = next(route_file_generator)

                # status = connection_geoserver.upload_style(
                #    path=route_file,
                #    workspace=StyleManager.workpace_name,
                # )
                #
                # print(status)

                StyleManager.post_upload_style(
                    file_path=route_file,
                    geoserver_ip=geoserver_ip,
                    geoserver_auth=geoserver_params
                )

                # get the table's name to publish style
                object_name = StyleManager.get_table_to_publish_styles(
                    geoserver_ip
                )
                
                StyleManager.serialize_style_information(connection_geoserver,geoserver_ip)

                # if has more than one table with the same style
                for count in range(len(object_name)):

                    status = connection_geoserver.publish_style(
                        layer_name=object_name[count].get('object_name'),
                        style_name=StyleManager.style_name,
                        workspace=StyleManager.workpace_name
                    )
                    print("status code: %s \ntable with the style:%s " %
                          (status, object_name[count].get('object_name')))

            except StopIteration:
                validator = False

    @classmethod
    def serialize_style_information(cls,connection,geoserver_ip):
        """Method to serialize style information (name, workspace,link)
        
        Params:
            connection (object): Object to connect with geoserver
            geoserver_ip (string): Which geoserver this routine may connect
        """

        print('STORE STYLE INFORMATION')
        workspaces_dict = Metadata.objects.filter(
            geoserver_ip=geoserver_ip
        ).exclude(
            geoserver_style_uri='None'
        ).values(
            "geoserver_workspace",
            "geoserver_style_uri",
            "style_name"
        )
        for workspace_name in workspaces_dict:

            instance = Workspaces.objects.get(geoserver_workspace=workspace_name.get('geoserver_workspace'))
            response, obj = Style.objects.filter(
                geoserver_workspace=instance,
                geoserver_style= workspace_name.get('geoserver_style_uri'),
                style_name=workspace_name.get('style_name')
            ).get_or_create(
                geoserver_workspace=instance,
                geoserver_style= workspace_name.get('geoserver_style_uri'),
                style_name=workspace_name.get('style_name')
            )
            
            if obj is False:
                response.save()
            elif obj is True:
                print("Style %s alredy exists, we'll modify" %(workspace_name.get('style_name')))
                Style.objects.filter(
                    geoserver_workspace=instance,
                    geoserver_style= workspace_name.get('geoserver_style_uri'),
                    style_name=workspace_name.get('style_name')
                ).delete()
                Style.objects.create(
                    geoserver_workspace=instance,
                    geoserver_style= workspace_name.get('geoserver_style_uri'),
                    style_name=workspace_name.get('style_name')
                ).save()
                continue

    @classmethod
    def get_style_link(cls, geoserver_ip):
        """Method to get the style link on metadata and your name
        ARGS:
            geoserver_ip (string) : Ip of geoserver
        RETURN:
            route (generator): path to sld file
        """

        styles_dict = Metadata.objects.filter(
            geoserver_ip=geoserver_ip
        ).exclude(
            geoserver_style_uri='None'
        ).values(
            "geoserver_workspace",
            "geoserver_style_uri",
            "style_name"
        )
        print("\nSTYLES ON %s To Verificate: \n%s\n" %
              (geoserver_ip, styles_dict)
              )

        for count in range(len(styles_dict)):
            StyleManager.style_name = styles_dict[count].get('style_name')

            StyleManager.geoserver_style_name = styles_dict[count].get(
                'geoserver_style_uri')

            StyleManager.workpace_name = styles_dict[count].get(
                'geoserver_workspace')
            route = os.path.join('/app/styles', StyleManager.style_name)

            if '0.0.0.0:443' in styles_dict[count].get('geoserver_style_uri') or 'gitlab' in styles_dict[count].get('geoserver_style_uri'):
                print('STYLE ON GITLAB')
                print(styles_dict[count].get('geoserver_style_uri'))
                data = requests.get(styles_dict[count].get('geoserver_style_uri') + '/raw?ref=main&private_token=%s' %(os.environ.get('gitlab_private_token')))
                print(data)

            elif 'http://' in styles_dict[count].get('geoserver_style_uri') or 'https://storage' in styles_dict[count].get('geoserver_style_uri'):
                print('STYLE ON STORAGE')
                print(styles_dict[count].get('geoserver_style_uri'))
                data = requests.get(styles_dict[count].get('geoserver_style_uri'))
                print(data)
            else:
                print("STYLE ON ANOTHER PLACE")
                data = requests.get('http://' + styles_dict[count].get('geoserver_style_uri'))
                print(data)

            with open(route, 'w') as file:
                file.write(data.content.decode("utf8"))

            yield route

    @classmethod
    def get_table_to_publish_styles(cls, geoserver_ip):
        """METHOD to publish styles, acording with layer
        ARGS:
            geoserver_ip (string) : Ip of geoserver
        """

        object_name = Metadata.objects.filter(
            geoserver_ip=geoserver_ip,
            geoserver_style_uri=StyleManager.geoserver_style_name
        ).values("object_name")

        return object_name


    @classmethod
    def post_upload_style(cls, file_path, geoserver_ip, geoserver_auth):
        """Method to upload the style on geoserver
        ARGS:
            geoserver_ip (string) : Ip of geoserver
            file_path (string) : path to sld file
        """
        host = 'http://'+ geoserver_ip + "/rest/workspaces/" + StyleManager.workpace_name + "/styles"
        print(host)

        session = requests.Session()
        params = (
            ('name', StyleManager.style_name),
        )

        tuple_authentication = (
            geoserver_auth['name'],
            geoserver_auth['password']
        )

        with open(file_path, 'r') as f:
            style = f.read()
        session.post(
            url=host,
            params=params,
            data=style,
            auth=tuple_authentication,
            headers={'Content-type': 'application/vnd.ogc.se+xml'}
        )
        session.close()
        print("Style Name %s  ^- OK" % file_path)
