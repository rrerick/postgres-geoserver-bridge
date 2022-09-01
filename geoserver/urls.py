from django.template import Context
from django.urls import path, re_path
from . import views

app_name='geoserver'
urlpatterns=[

    path('api/', views.RedirectRetriewView.as_view(), name='workspaces')
]