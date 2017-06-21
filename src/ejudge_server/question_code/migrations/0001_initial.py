# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-14 02:52
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IoQuestion',
            fields=[
                ('title', models.CharField(
                    help_text="IoQuestion's name", max_length=100)),
                ('uuid', models.UUIDField(default=uuid.uuid4,
                                          help_text='Universal Unique Identifier.', primary_key=True, serialize=False)),
                ('source', models.TextField(
                    help_text='Source code for the reference solution used to expand the iospec template.')),
                ('language', models.CharField(choices=[('python', 'Python 3.x'), ('python2', 'Python 2.7'), (
                    'gcc', 'C (gcc 6.3 --std=c99)')], help_text='Programming language used in the reference program.', max_length=50)),
                ('iospec', models.TextField(blank=True, editable=False,
                                            help_text='Expanded iospec data. Use the ./iospec-expansion/ endpoint in order to force/control expansion')),
                ('iospec_template', models.TextField(
                    help_text='Correction template written in the iospec format.')),
                ('num_expansions', models.IntegerField(
                    default=25, help_text='Default number of expansions computed from the iospec template.')),
                ('is_valid', models.BooleanField(default=bool)),
            ],
        ),
        migrations.CreateModel(
            name='IoSubmission',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4,
                                          primary_key=True, serialize=False)),
                ('source', models.TextField(help_text='Source code for submission.')),
                ('language', models.CharField(choices=[('python', 'Python 3.x'), ('python2', 'Python 2.7'), (
                    'gcc', 'C (gcc 6.3 --std=c99)')], help_text='Programming language used in the submitted program.', max_length=50)),
                ('has_feedback', models.BooleanField(
                    default=bool, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='IoFeedback',
            fields=[
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                                    primary_key=True, related_name='feedback', serialize=False, to='question_io.IoSubmission')),
                ('grade', models.DecimalField(decimal_places=2, max_digits=5, validators=[
                 django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('feedback_data', jsonfield.fields.JSONField()),
            ],
        ),
        migrations.AddField(
            model_name='iosubmission',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='submissions', to='question_io.IoQuestion'),
        ),
    ]
