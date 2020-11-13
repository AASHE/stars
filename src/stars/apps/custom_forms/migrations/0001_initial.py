# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataDisplayAccessRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=128)),
                ('affiliation', models.CharField(max_length=128, verbose_name=b'Institution or Affiliation')),
                ('city_state', models.CharField(max_length=64, verbose_name=b'City/State')),
                ('email', models.EmailField(max_length=75)),
                ('summary', models.TextField(verbose_name=b'Summary description of your research')),
                ('how_data_used', models.TextField(verbose_name=b'How will STARS data be used in your research?')),
                ('will_publish', models.BooleanField(default=False, verbose_name=b'Click here if you will be distributing or publishing the data?')),
                ('audience', models.TextField(verbose_name=b'Who is the intended audience for your research?')),
                ('period', models.DateField(verbose_name=b'Requesting access starting on this date (mm/dd/yyyy)')),
                ('end', models.DateField(verbose_name=b'Access requested until (mm/dd/yyyy)')),
                ('has_instructor', models.BooleanField(default=False, verbose_name=b'Is there an academic instructor or advisor who will provide guidance on how this data will be used?')),
                ('instructor', models.TextField(null=True, verbose_name=b'If yes, list name of instructor, title of instructor, and e-mail address.', blank=True)),
                ('date', models.DateField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EligibilityQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=75)),
                ('institution', models.CharField(max_length=128)),
                ('requesting_institution', models.CharField(max_length=128, null=True, blank=True)),
                ('other_affiliates', models.BooleanField(default=False)),
                ('included_in_boundary', models.BooleanField(default=False)),
                ('separate_administration', models.BooleanField(default=False)),
                ('rationale', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SteeringCommitteeNomination',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=16)),
                ('last_name', models.CharField(max_length=16)),
                ('email', models.EmailField(max_length=75)),
                ('affiliation', models.CharField(max_length=128, verbose_name=b'Institution or Affiliation')),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('why', models.TextField(verbose_name=b'Why would you be excited to serve on the STARS Steering Committee?')),
                ('skills', models.TextField(verbose_name=b'What specific skills or background would you bring to the STARS Steering Committee that would help advance STARS?')),
                ('successful', models.TextField(verbose_name=b'How can you help STARS become a successful rating system?')),
                ('strengths', models.TextField(verbose_name=b'What do you consider to be the strengths and weaknesses of STARS?')),
                ('perspectives', models.TextField(verbose_name=b'What perspectives or representation of stakeholder groups would you bring to the STARS Steering Committee?')),
                ('resume', models.FileField(max_length=255, upload_to=b'sc_apps')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TAApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=16)),
                ('last_name', models.CharField(max_length=16)),
                ('title', models.CharField(max_length=64)),
                ('department', models.CharField(max_length=64)),
                ('institution', models.CharField(max_length=128, verbose_name=b'Institution/Organization Affiliation')),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('email', models.EmailField(max_length=75)),
                ('instituion_type', models.CharField(max_length=32, verbose_name=b'Institution/Organization Type', choices=[(b'2-year', b"2-year Associate's College"), (b'baccalaureate', b'Baccalaureate College'), (b'masters', b"Master's Institution"), (b'research', b'Research University'), (b'non-profit', b'Non-profit Organization'), (b'gov', b'Government Agency'), (b'for-profit', b'For-profit Business'), (b'other', b'Other')])),
                ('skills_and_experience', models.TextField()),
                ('related_associations', models.TextField()),
                ('resume', models.FileField(max_length=255, upload_to=b'ta_apps')),
                ('credit_weakness', models.TextField(null=True, blank=True)),
                ('date_registered', models.DateTimeField(auto_now_add=True)),
                ('subcategories', models.ManyToManyField(to='credits.Subcategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
