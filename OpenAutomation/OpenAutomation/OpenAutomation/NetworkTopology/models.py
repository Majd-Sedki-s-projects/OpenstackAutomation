from django.db import models
from django_mysql.models import JSONField
from django.core import serializers


class Topology(models.Model):
    topology_name = models.CharField(max_length=25, default="No_Name_Provided")
    topology_json = JSONField()

    class Meta:
        app_label = "NetworkTopology"

    def __str__(self):
        return self.topology_name
