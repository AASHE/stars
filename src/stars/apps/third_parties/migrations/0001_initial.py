# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdParty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=16)),
                ('name', models.CharField(max_length=64)),
                ('publication', models.CharField(max_length=128, null=True, blank=True)),
                ('logo', models.ImageField(null=True, upload_to=b'tps', blank=True)),
                ('next_deadline', models.DateField(null=True, blank=True)),
                ('disabled', models.BooleanField(default=False)),
                ('help_text', models.TextField(null=True, blank=True)),
                ('access_to_institutions', models.ManyToManyField(related_name='third_parties', null=True, to='institutions.Institution', blank=True)),
                ('authorized_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-next_deadline'],
                'verbose_name_plural': 'Third Parties',
            },
            bases=(models.Model,),
        ),
    ]
