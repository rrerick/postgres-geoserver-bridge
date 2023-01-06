from django.urls import path
from . import views

app_name = 'geoserver'
urlpatterns = [
    path('', views.RedirectRetriewView.as_view(), name='workspaces')
]
