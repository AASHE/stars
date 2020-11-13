# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorizedUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('member_level', models.BooleanField(default=False)),
                ('participant_level', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-start_date', '-end_date'),
            },
            bases=(models.Model,),
        ),
    ]
