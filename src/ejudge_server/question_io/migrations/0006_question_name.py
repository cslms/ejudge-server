# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-14 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_io', '0005_auto_20170314_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='name',
            field=models.CharField(default='test question', max_length=100),
            preserve_default=False,
        ),
    ]