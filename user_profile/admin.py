from django.contrib import admin

# Register your models here.
from . import models

admin.site.register([models.UsersGeoserver,  models.Pg_User, models.create_pg_user])
admin.site.register(models.Token)
