from django.db import models

# Create your models here.


class Metadata (models.Model):
    """ Table to store metadata information
    """
    object_name = models.CharField(max_length=200)
    schema_name = models.CharField(max_length=200)
    geoserver_title = models.CharField(max_length=200, default='null')
    geoserver_style_uri = models.CharField(max_length=200, default='null')
    geoserver_workspace = models.CharField(max_length=200,default='null')
    geoserver_ip = models.CharField(max_length=200, default='null')
    style_name = models.CharField(max_length=200,default='st_with_no_name')
    data_insercao = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.object_name
    class Meta:
        db_table = 'tb_metadata_geoserver'
        verbose_name = 'metadado'

class Workspaces(models.Model):
    """Table to store registered workspaces
    """
    geoserver_workspace = models.CharField(max_length=200,default='null')
    geoserver_ip =models.CharField(max_length=200,default='null')
    data_insercao = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.geoserver_workspace

    class Meta:
        db_table = 'tb_geoserver_workspces'

class Store(models.Model):
    """Table to store registered datastores
    """
    geoserver_workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE)
    geoserver_store =models.CharField(max_length=200,default='null')
    data_insercao = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.geoserver_store

    class Meta:
        db_table = 'tb_geoserver_datastore'
        verbose_name = 'store'

class Style(models.Model):
    """Table to store registered styles
    """
    geoserver_workspace = models.ForeignKey(Workspaces,on_delete=models.CASCADE)
    geoserver_style = models.CharField(max_length=300,default='null')
    style_name =  models.CharField(max_length=300,default='null')
    data_insercao = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.geoserver_workspace

    class Meta:
        db_table = 'tb_geoserver_style'