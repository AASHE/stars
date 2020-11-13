# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent_date', models.DateTimeField(auto_now_add=True)),
                ('sent_to', models.CharField(max_length=128)),
                ('subject', models.CharField(max_length=128)),
                ('notification_type', models.CharField(max_length=7, choices=[(b'4wk', b'4 Weeks Late'), (b'6mn', b'6 months left'), (b'wel', b'Welcome')])),
                ('identifier', models.CharField(max_length=16)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
