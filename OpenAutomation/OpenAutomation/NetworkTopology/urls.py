from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.returnjson, name='index'),
   # url(r'^json/$', views.returnjson, name='returnjson'),
]
