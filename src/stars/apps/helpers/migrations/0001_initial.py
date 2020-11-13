# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(unique=True)),
                ('content', models.TextField()),
            ],
            options={
                'ordering': ('key',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HelpContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=64, null=True, blank=True)),
                ('help_text', models.TextField()),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SnippetContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(unique=True)),
                ('content', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('key',),
            },
            bases=(models.Model,),
        ),
    ]
