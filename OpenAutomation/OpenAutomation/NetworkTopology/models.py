from django.db import models
from django_mysql.models import JSONField


class Topology(models.Model):
    topology_name = models.CharField(max_length=25, default="No_Name_Provided")
    topology_json = JSONField()

    class Meta:
        app_label = "NetworkTopology"

    def __str__(self):
        return self.topology_name


class NetworkApplications(models.Model):
    application_name = models.CharField(max_length=25, default="NO_APP_NAME_PROVIDED")
    application_requirements = JSONField()
    application_os = models.CharField(max_length=25, default="NO_OS_SPECIFIED")

    class Meta:
        app_label = "NetworkTopology"

    def __str__(self):
        return self.application_name
