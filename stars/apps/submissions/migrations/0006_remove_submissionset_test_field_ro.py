# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2020-07-15 13:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0005_submissionset_test_field_ro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionset',
            name='test_field_ro',
        ),
    ]
