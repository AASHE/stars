# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentationfield',
            name='ordinal',
            field=models.FloatField(default=-1.0, db_index=True),
            preserve_default=True,
        ),
    ]
