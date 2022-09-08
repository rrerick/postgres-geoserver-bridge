from django.db import models
from django.contrib.auth.hashers import make_password
from cryptography.fernet import Fernet
from django.dispatch import receiver
from django.db.models.signals import post_save

from geoserver_management.settings import SECURITY_FILE

# Create your models here.
class create_pg_user(models.Model):
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

    class Meta:
        verbose_name = 'Create Database information'

@receiver(post_save, sender=create_pg_user)
def signal_receiver(sender, instance, **kwargs):

    key = Fernet.generate_key()
    pub_key = key.decode()
    f = Fernet(key)
    token = f.encrypt(instance.password.encode())

    Pg_User.objects.create(
        username = instance.username,
        token = token.decode(),
        pub_key = pub_key,
        dbname = instance.dbname,
        ip = instance.ip,
        port = instance.port
    )
    instance.delete()


class Pg_User(models.Model):
    """This model contains user, password, host, port about user in database
    """
    username = models.CharField(
        max_length=200
    )
    pub_key = models.CharField(
        max_length=500,
        blank=True
    )
    token = models.CharField(
        max_length=300,
        blank=True
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


    def __str__(self):
        return 'User Db: %s | DBNAME: %s' %(self.username,self.dbname)
    def save(self, *args, **kwargs):
        return super(Pg_User, self).save( *args, **kwargs)
    class Meta:
        verbose_name = 'Pg_User'


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
    key = models.CharField(
        max_length=500,
        blank=True
    )

    pub_key = models.CharField(
        max_length=500,
        blank=True,
    )

    def save(self, *args, **kwargs):
        """Before save encript the geoserver passoword
        """
        key = Fernet.generate_key()
        f = Fernet(key)

        self.pub_key = key

        new_password = self.geoserver_password.encode()
        token = f.encrypt(new_password)
        self.key= token

        return super(UsersGeoserver, self).save(*args, **kwargs)
    class Meta:
        verbose_name = "Create Geoserve's User"

class Token(models.Model):
    ip = models.CharField(
        max_length=200
    )
    user = models.CharField(max_length=300)
    token = models.CharField(max_length=500)
    pub_key = models.CharField(max_length=500)
    def __str__(self):
        return "USER: %s | IP: %s" %(self.user, self.ip )
    class Meta:
        verbose_name = "Geoserver's User"

@receiver(post_save, sender=UsersGeoserver)
def signal_receiver_security_data(sender, instance, **kwargs):
    Token.objects.create(
        token = instance.key.decode(),
        user = instance.geoserver_user,
        pub_key = instance.pub_key.decode('utf-8'),
        ip = instance.geoserver_ip
    )
    instance.delete()