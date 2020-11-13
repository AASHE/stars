# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stars.apps.submissions.models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionset',
            name='pdf_report',
            field=models.FileField(max_length=255, null=True, upload_to=stars.apps.submissions.models.submission_upload_path_callback, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='submissionset',
            name='presidents_letter',
            field=models.FileField(upload_to=stars.apps.submissions.models.submission_upload_path_callback, max_length=255, blank=True, help_text=b"Please upload a letter from your institution's president, chancellor or other high ranking executive in PDF format.", null=True, verbose_name=b'Executive Letter'),
            preserve_default=True,
        ),
    ]
