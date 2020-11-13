# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInvite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BaseAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClimateZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('enabled', models.BooleanField(default=True, help_text=b'This is a staff-only flag for disabling an institution. An institution will NOT appear on the STARS Institutions list until it is enabled.')),
                ('contact_first_name', models.CharField(max_length=32, verbose_name=b'Liaison First Name')),
                ('contact_middle_name', models.CharField(max_length=32, null=True, verbose_name=b'Liaison Middle Name', blank=True)),
                ('contact_last_name', models.CharField(max_length=32, verbose_name=b'Liaison Last Name')),
                ('contact_title', models.CharField(max_length=255, null=True, verbose_name=b'Liaison Title', blank=True)),
                ('contact_department', models.CharField(max_length=64, null=True, verbose_name=b'Liaison Department', blank=True)),
                ('contact_email', models.EmailField(max_length=75, null=True, verbose_name=b'Liaison Email', blank=True)),
                ('executive_contact_first_name', models.CharField(max_length=32, null=True, blank=True)),
                ('executive_contact_middle_name', models.CharField(max_length=32, null=True, blank=True)),
                ('executive_contact_last_name', models.CharField(max_length=32, null=True, blank=True)),
                ('executive_contact_title', models.CharField(max_length=64, null=True, blank=True)),
                ('executive_contact_department', models.CharField(max_length=64, null=True, blank=True)),
                ('executive_contact_email', models.EmailField(max_length=75, null=True, blank=True)),
                ('executive_contact_address', models.CharField(max_length=128, null=True, blank=True)),
                ('executive_contact_city', models.CharField(max_length=16, null=True, blank=True)),
                ('executive_contact_state', models.CharField(max_length=2, null=True, blank=True)),
                ('executive_contact_zip', models.CharField(max_length=8, null=True, blank=True)),
                ('president_first_name', models.CharField(max_length=32, null=True, blank=True)),
                ('president_middle_name', models.CharField(max_length=32, null=True, blank=True)),
                ('president_last_name', models.CharField(max_length=32, null=True, blank=True)),
                ('president_title', models.CharField(max_length=64, null=True, blank=True)),
                ('president_email', models.EmailField(max_length=75, null=True, blank=True)),
                ('president_address', models.CharField(max_length=128, null=True, blank=True)),
                ('president_city', models.CharField(max_length=32, null=True, blank=True)),
                ('president_state', models.CharField(max_length=2, null=True, blank=True)),
                ('president_zip', models.CharField(max_length=8, null=True, blank=True)),
                ('charter_participant', models.BooleanField(default=False)),
                ('stars_staff_notes', models.TextField(null=True, blank=True)),
                ('date_created', models.DateTimeField(db_index=True, auto_now_add=True, null=True)),
                ('international', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255)),
                ('aashe_id', models.IntegerField(unique=True, null=True, blank=True)),
                ('fte', models.IntegerField(null=True, blank=True)),
                ('is_pcc_signatory', models.NullBooleanField(default=False)),
                ('is_member', models.NullBooleanField(default=False)),
                ('is_pilot_participant', models.NullBooleanField(default=False)),
                ('country', models.CharField(max_length=128, null=True, blank=True)),
                ('institution_type', models.CharField(max_length=128, null=True, blank=True)),
                ('rating_expires', models.DateField(null=True, blank=True)),
                ('prefers_metric_system', models.BooleanField(default=False)),
                ('is_test_institution', models.BooleanField(default=False, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstitutionPreferences',
            fields=[
                ('institution', models.OneToOneField(related_name='preferences', primary_key=True, serialize=False, editable=False, to='institutions.Institution')),
                ('notify_users', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MigrationHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('institution', models.ForeignKey(to='institutions.Institution')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PendingAccount',
            fields=[
                ('baseaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='institutions.BaseAccount')),
                ('terms_of_service', models.BooleanField(default=False)),
                ('user_level', models.CharField(max_length=b'6', verbose_name=b'Role', choices=[(b'admin', b'Administrator'), (b'submit', b'Data Entry'), (b'view', b'Observer')])),
                ('user_email', models.EmailField(max_length=75)),
                ('institution', models.ForeignKey(to='institutions.Institution')),
            ],
            options={
            },
            bases=('institutions.baseaccount',),
        ),
        migrations.CreateModel(
            name='RegistrationReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistrationSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.TextField(null=True, verbose_name=b'How did you hear about STARS?', blank=True)),
                ('other', models.CharField(max_length=64, null=True, blank=True)),
                ('enhancements', models.TextField(null=True, verbose_name=b'Is there anything AASHE can do or provide to improve your experience using STARS (resources, trainings, etc.)?', blank=True)),
                ('institution', models.ForeignKey(to='institutions.Institution')),
                ('primary_reason', models.ForeignKey(related_name='primary_surveys', blank=True, to='institutions.RegistrationReason', null=True)),
                ('reasons', models.ManyToManyField(to='institutions.RegistrationReason', null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RespondentRegistrationReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RespondentSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.TextField(null=True, verbose_name=b'How did you hear about the CSDC?', blank=True)),
                ('other', models.CharField(max_length=64, null=True, blank=True)),
                ('potential_stars', models.NullBooleanField(verbose_name=b'Is your institution considering registering as a STARS participant?')),
                ('institution', models.ForeignKey(to='institutions.Institution')),
                ('reasons', models.ManyToManyField(to='institutions.RespondentRegistrationReason', null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StarsAccount',
            fields=[
                ('baseaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='institutions.BaseAccount')),
                ('terms_of_service', models.BooleanField(default=False)),
                ('user_level', models.CharField(max_length=b'6', verbose_name=b'Role', choices=[(b'admin', b'Administrator'), (b'submit', b'Data Entry'), (b'view', b'Observer')])),
                ('is_selected', models.BooleanField(default=False)),
                ('institution', models.ForeignKey(to='institutions.Institution')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('institutions.baseaccount',),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ms_id', models.CharField(max_length=64, null=True, blank=True)),
                ('name', models.CharField(max_length=512, null=True, blank=True)),
                ('start_date', models.DateField(db_index=True)),
                ('end_date', models.DateField(db_index=True)),
                ('access_level', models.CharField(default=b'Basic', max_length=8, choices=[(b'Basic', b'Basic'), (b'Full', b'Full')])),
                ('ratings_allocated', models.SmallIntegerField(default=1)),
                ('ratings_used', models.IntegerField(default=0)),
                ('amount_due', models.FloatField(default=0)),
                ('reason', models.CharField(max_length=b'16', null=True, blank=True)),
                ('paid_in_full', models.BooleanField(default=False)),
                ('late', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False, db_index=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='institutions.Institution', null=True)),
            ],
            options={
                'ordering': ['-start_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('method', models.CharField(max_length=b'8', choices=[(b'credit', b'credit'), (b'check', b'check')])),
                ('confirmation', models.CharField(max_length=b'16', null=True, blank=True)),
                ('subscription', models.ForeignKey(to='institutions.Subscription')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='starsaccount',
            unique_together=set([('user', 'institution')]),
        ),
        migrations.AlterUniqueTogether(
            name='pendingaccount',
            unique_together=set([('user_email', 'institution')]),
        ),
    ]
