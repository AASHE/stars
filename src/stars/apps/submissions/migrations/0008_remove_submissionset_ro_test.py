# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-07-27 17:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0007_submissionset_ro_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionset',
            name='ro_test',
        ),
    ]
