# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0001_initial'),
        ('credits', '0001_initial'),
        ('institutions', '0001_initial'),
        ('iss', '0009_add_field_organization_institution_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='migrationhistory',
            name='source_ss',
            field=models.ForeignKey(related_name='migration_sources', to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='migrationhistory',
            name='target_ss',
            field=models.ForeignKey(related_name='migration_targets', to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='current_rating',
            field=models.ForeignKey(blank=True, to='credits.Rating', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='current_submission',
            field=models.ForeignKey(related_name='current', blank=True, to='submissions.SubmissionSet', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='current_subscription',
            field=models.ForeignKey(related_name='current', blank=True, to='institutions.Subscription', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='latest_expired_submission',
            field=models.ForeignKey(related_name='latest_expired', blank=True, to='submissions.SubmissionSet', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='rated_submission',
            field=models.ForeignKey(related_name='rated', blank=True, to='submissions.SubmissionSet', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='MemberSuiteInstitution',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('iss.organization',),
        ),
        migrations.AddField(
            model_name='institution',
            name='ms_institution',
            field=models.OneToOneField(null=True, blank=True, to='institutions.MemberSuiteInstitution'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='ms_institution',
            field=models.ForeignKey(blank=True, to='institutions.MemberSuiteInstitution', null=True),
            preserve_default=True,
        ),
    ]
