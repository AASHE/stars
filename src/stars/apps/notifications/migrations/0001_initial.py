# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CopyEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.EmailField(max_length=75)),
                ('bcc', models.BooleanField(default=False, help_text=b'Check to copy this user using BCC')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'Unique name. Please do not change.', unique=True, max_length=32)),
                ('title', models.CharField(help_text=b'The subjuect line of the email.', max_length=128)),
                ('description', models.TextField()),
                ('content', models.TextField()),
                ('example_data', jsonfield.fields.JSONField(help_text=b'Example context for the template. Do not change.', null=True, blank=True)),
                ('active', models.BooleanField(default=False, help_text=b"Checked indicates that the code is using this email. For Webdev's use only")),
            ],
            options={
                'ordering': ('slug',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='copyemail',
            name='template',
            field=models.ForeignKey(to='notifications.EmailTemplate'),
            preserve_default=True,
        ),
    ]
