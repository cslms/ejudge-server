# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-14 19:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('question_io', '0003_auto_20170314_1714'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grader',
            options={'ordering': ['created']},
        ),
        migrations.AddField(
            model_name='grader',
            name='created',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2017, 3, 14, 19, 29, 39, 644173, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='grader',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='graders', to='question_io.Question'),
        ),
    ]
