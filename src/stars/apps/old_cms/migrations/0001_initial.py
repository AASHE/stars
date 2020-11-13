# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.SmallIntegerField(default=0)),
                ('published', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField(help_text=b'This is a URL-friendly version of the title. Do not change unless you want to change the link')),
                ('content', models.TextField(help_text=b'If left blank, the page will be populated with the teaser text from all the articles.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HomepageUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.SmallIntegerField(default=0)),
                ('published', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('link', models.URLField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('ordinal', 'title', 'timestamp'),
                'verbose_name': 'Homepage Update',
                'verbose_name_plural': 'Homepage Updates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.SmallIntegerField(default=0)),
                ('published', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('content', models.TextField()),
                ('teaser', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('irc_id', models.IntegerField(help_text=b'Only necessary for pages that used to exist in the IRC. New pages will not need this.', null=True, blank=True)),
                ('categories', models.ManyToManyField(to='old_cms.Category', null=True, blank=True)),
            ],
            options={
                'ordering': ('ordinal', 'title', 'timestamp'),
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.SmallIntegerField(default=0)),
                ('published', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField(help_text=b'This is a URL-friendly version of the title. Do not change unless you want to change the link')),
                ('content', models.TextField(help_text=b'If left blank, the page will be populated with the teaser text from all the articles.', null=True, blank=True)),
                ('parent', models.ForeignKey(to='old_cms.Category')),
            ],
            options={
                'verbose_name_plural': 'Subcategories',
            },
            bases=(models.Model,),
        ),
    ]
