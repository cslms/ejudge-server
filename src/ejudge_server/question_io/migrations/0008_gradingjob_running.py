# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-14 20:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_io', '0007_auto_20170314_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradingjob',
            name='running',
            field=models.BooleanField(default=bool),
        ),
    ]
