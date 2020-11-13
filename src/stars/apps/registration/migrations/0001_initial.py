# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ValueDiscount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=36)),
                ('amount', models.PositiveIntegerField(help_text=b'Discount Amount')),
                ('applicability_filter', models.TextField(blank=True)),
                ('automatic', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=78, blank=True)),
                ('percentage', models.PositiveIntegerField(default=0, help_text=b'Discount Percentage', validators=[django.core.validators.MaxValueValidator(100)])),
                ('start_date', models.DateField(help_text=b'Valid From')),
                ('end_date', models.DateField(help_text=b'Valid Until')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
