# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-22 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NetworkTopology', '0005_networkapplications_application_config_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='networkapplications',
            name='application_config_file',
        ),
        migrations.AddField(
            model_name='networkapplications',
            name='application_os',
            field=models.CharField(default='NO_OS_SPECIFIED', max_length=25),
        ),
    ]
