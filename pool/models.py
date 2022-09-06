from django.db import models

# Create your models here.


class Metadata (models.Model):
    object_name = models.CharField(max_length=200)
    schema_name = models.CharField(max_length=200)
    geoserver_title = models.CharField(max_length=200, default='null')
    geoserver_style_uri = models.CharField(max_length=200, default='null')
    geoserver_workspace = models.CharField(max_length=200,default='null')
    geoserver_ip = models.CharField(max_length=200, default='null')
    def __str__(self):
        return self.object_name
    class Meta:
        db_table = 'tb_metadata_geoserver'
        verbose_name = 'metadado'

class Workspaces(models.Model):
    geoserver_workspace =models.CharField(max_length=200,default='null')

    def __str__(self):
        return self.geoserver_workspace

    class Meta:
        db_table = 'tb_geoserver_workspces'