from django.db import models

# Create your models here.


class INPEGeoserverCopy (models.Model):
    data=models.JSONField()

