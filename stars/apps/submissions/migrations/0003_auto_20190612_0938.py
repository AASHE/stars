# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-06-12 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0002_auto_20181214_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditsubmissionreviewnotation',
            name='kind',
            field=models.CharField(choices=[(b'best-practice', b'Best Practice'), (b'revision-request', b'Revision Request'), (b'suggestion-for-improvement', b'Suggestion For Improvement')], max_length=32),
        ),
        migrations.AlterField(
            model_name='multichoicesubmission',
            name='value',
            field=models.ManyToManyField(blank=True, to='credits.Choice'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='confirmation',
            field=models.CharField(blank=True, help_text=b'The CC confirmation code or check number', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='reason',
            field=models.CharField(choices=[(b'member_reg', b'member_reg'), (b'nonmember_reg', b'nonmember_reg'), (b'member_renew', b'member_renew'), (b'nonmember_renew', b'nonmember_renew'), (b'international', b'international')], max_length=16),
        ),
        migrations.AlterField(
            model_name='payment',
            name='type',
            field=models.CharField(choices=[(b'credit', b'credit'), (b'check', b'check'), (b'later', b'pay later')], max_length=8),
        ),
        migrations.AlterField(
            model_name='responsibleparty',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='submissioninquiry',
            name='email_address',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
