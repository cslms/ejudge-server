# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-12 21:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_io', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grader',
            name='num_expansiosn',
            field=models.IntegerField(default=20),
        ),
        migrations.AddField(
            model_name='question',
            name='num_expansiosn',
            field=models.IntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='grader',
            name='iospec_post',
            field=models.TextField(blank=True),
        ),
    ]
