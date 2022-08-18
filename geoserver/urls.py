from django.template import Context
from django.urls import path, re_path
from . import views

app_name='geoserver'
urlpatterns=[

    path('',views.connection_geoserver_db, name='connection')
]