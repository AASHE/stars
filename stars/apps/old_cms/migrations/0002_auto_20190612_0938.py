# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-06-12 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('old_cms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newarticle',
            name='categories',
            field=models.ManyToManyField(blank=True, to='old_cms.Category'),
        ),
    ]
