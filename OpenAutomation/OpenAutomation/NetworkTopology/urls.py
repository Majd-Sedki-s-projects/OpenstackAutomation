from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='Home'),
    url(r'^NetworkTopology/$', views.network_topology, name='NetworkTopology'),
    url(r'^Admin/$', views.admin, name='admin'),
    url(r'^Contact/$', views.contact, name='contact'),
    #url(r'^upload_file/$', views.upload_file, name='upload_file'),
]
