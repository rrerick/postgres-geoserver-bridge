from django.db import models

import os
import jwt


# Create your models here.
class Pg_User(models.Model):
    """This model is just to create database infos
    after creating the info gonna be delete
    """
    username = models.CharField(
        max_length=200
    )
    password = models.CharField(
        max_length=200
    )
    dbname = models.CharField(
        max_length=200
    )
    ip = models.CharField(
        max_length=100
    )
    port = models.CharField(
        max_length=10
    )
    authtk = models.CharField(
        max_length=400,
        blank=True
    )
    class Meta:
        verbose_name = 'PostgreSql User'
    
    def save(self, *args, **kwargs):
        payload_data = {
            "sub":"db_info",
            "name":self.username,
            "password":self.password
        }
        my_secret = os.getenv('secret')
        self.authtk = jwt.encode(
            payload=payload_data,
            key=my_secret
        )
        self.password = 'null'
        return super().save(*args, **kwargs)
    def __str__(self):
        return 'User Db: %s | DBNAME: %s' %(self.username,self.dbname)


class UsersGeoserver (models.Model):
    geoserver_ip = models.CharField(
        max_length=200
    )
    geoserver_user = models.CharField(
        max_length=50
    )
    geoserver_password = models.CharField(
        max_length=200
    )
    authtk = models.CharField(
        max_length=400,
        blank=True
    )

    def save(self, *args, **kwargs):

        if ('http://' in self.geoserver_ip):
            self.geoserver_ip = self.geoserver_ip.replace('http://', '')
        elif ('https://' in self.geoserver_ip):
            self.geoserver_ip = self.geoserver_ip.replace('https://', '')
        else:
            self.geoserver_ip = self.geoserver_ip

        payload_data = {
            "sub":"geoserver_user",
            "name":self.geoserver_user,
            "password":self.geoserver_password
        }
        my_secret = os.getenv('secret')
        self.authtk = jwt.encode(
            payload=payload_data,
            key=my_secret
        )
        self.geoserver_password = 'null'
        return super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Geoserve's User"
    def __str__(self):
        return self.geoserver_ip
