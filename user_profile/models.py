from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from cryptography.fernet import Fernet
from django.dispatch import receiver
from django.db.models.signals import post_save

from geoserver_automator.settings import SECURITY_FILE

# Create your models here.
class create_pg_user(models.Model):
    """This model is just to create pg_user
    after creating the info gonna be delete
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    username = models.CharField(
        max_length=200
    )
    password = models.CharField(
        max_length=200
    )

    class Meta:
        verbose_name = 'create Pg_User'

@receiver(post_save, sender=create_pg_user)
def signal_receiver(sender, instance, **kwargs):

    key = Fernet.generate_key()
    pub_key = key.decode()
    f = Fernet(key)
    token = f.encrypt(instance.password.encode())

    Pg_User.objects.create(
        owner = instance.owner,
        username = instance.username,
        token = token.decode(),
        pub_key = pub_key
    )
    instance.delete()


class Pg_User(models.Model):
    """This model contains user, password, host, port about user in database
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
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

    def __str__(self):
        return '%s | %s' %(self.username,str(self.owner))
    def save(self, *args, **kwargs):
        return super(Pg_User, self).save( *args, **kwargs)
    class Meta:
        verbose_name = 'Pg_User'

class Db_info(models.Model):
    """Model about Database information,
    and user to connect with(pg_user_name)
    """
    pg_user_name = models.ForeignKey(
        Pg_User,
        on_delete=models.CASCADE
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
        return '%s | %s' %(self.dbname, self.ip)

    class Meta:
        verbose_name = 'Database Info'

class UsersGeoserver (models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    geoserver_ip = models.CharField(
        max_length=200
    )
    geoserver_user = models.CharField(
        max_length=50
    )
    geoserver_password = models.CharField(
        max_length=200
    )
    repeat_password = models.CharField(
        max_length=200,
    )
    key = models.CharField(
        max_length=500,
        blank=True
    )

    other_key = models.CharField(
        max_length=500,
        blank=True,
    )

    def save(self, *args, **kwargs):
        """Before save encript the geoserver passoword
        """
        key = Fernet.generate_key()
        f = Fernet(key)

        self.other_key = key

        new_password = self.repeat_password.encode()
        token = f.encrypt(new_password)
        self.key= token
        self.geoserver_password = make_password(self.geoserver_password)

        return super(UsersGeoserver, self).save(*args, **kwargs)
    class Meta:
        verbose_name = "Create Geoserve's User"

class Token(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    ip = models.CharField(
        max_length=200
    )
    token = models.CharField(max_length=500)
    user = models.CharField(max_length=300)
    pub_key = models.CharField(max_length=500)
    def __str__(self):
        return "%s | owner: %s" %(self.user, str(self.owner))
    class Meta:
        verbose_name = "Geoserver's User"

@receiver(post_save, sender=UsersGeoserver)
def signal_receiver_security_data(sender, instance, **kwargs):
    Token.objects.create(
        owner = instance.owner,
        token = instance.key.decode(),
        user = instance.geoserver_user,
        pub_key = instance.other_key.decode('utf-8'),
        ip = instance.geoserver_ip
    )
    instance.delete()