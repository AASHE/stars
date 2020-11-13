# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
import stars.apps.submissions.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('credits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BooleanSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.NullBooleanField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Boundary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fte_students', models.IntegerField(null=True, verbose_name=b'Full-time Equivalent Enrollment', blank=True)),
                ('undergrad_count', models.IntegerField(null=True, verbose_name=b'Number of Undergraduate Students', blank=True)),
                ('graduate_count', models.IntegerField(null=True, verbose_name=b'Number of Graduate Students', blank=True)),
                ('fte_employmees', models.IntegerField(null=True, verbose_name=b'Full-time Equivalent Employees', blank=True)),
                ('institution_type', models.CharField(blank=True, max_length=32, null=True, choices=[(b'associate', b'Associate'), (b'baccalaureate', b'Baccalaureate'), (b'master', b'Master'), (b'doctorate', b'Doctorate'), (b'special_focus', b'Special Focus'), (b'tribal', b'Tribal')])),
                ('institutional_control', models.CharField(blank=True, max_length=32, null=True, choices=[(b'public', b'Public'), (b'private_profit', b'Private for-profit'), (b'private_nonprofit', b'Private non-profit')])),
                ('endowment_size', models.BigIntegerField(null=True, blank=True)),
                ('student_residential_percent', models.FloatField(null=True, verbose_name=b'Percentage of students that are Residential', blank=True)),
                ('student_ftc_percent', models.FloatField(help_text=b'Please indicate the percentage of full-time enrolled students that commute to campus.', null=True, verbose_name=b'Percentage of students that are Full-time commuter', blank=True)),
                ('student_ptc_percent', models.FloatField(help_text=b'Please indicate the percentage of part-time enrolled students that commute to campus.', null=True, verbose_name=b'Percentage of students that are Part-time commuter', blank=True)),
                ('student_online_percent', models.FloatField(null=True, verbose_name=b'Percentage of students that are On-line only', blank=True)),
                ('gsf_building_space', models.FloatField(help_text=b"For guidance, consult <a href='http://nces.ed.gov/pubs2006/ficm/content.asp?ContentType=Section&chapter=3&section=2&subsection=1' target='_blank'>3.2.1 Gross Area (Gross Square Feet-GSF)</a> of the U.S. Department of Education's Postsecondary Education Facilities Inventory and Classification Manual.", null=True, verbose_name=b'Gross square feet of building space', blank=True)),
                ('gsf_lab_space', models.FloatField(help_text=b'Scientific research labs and other high performance facilities eligible for <a href="http://www.labs21century.gov/index.htm" target="_blank">Labs21 Environmental Performance Criteria</a> (EPC).', null=True, verbose_name=b'Gross square feet of laboratory space', blank=True)),
                ('cultivated_grounds_acres', models.FloatField(help_text=b'Areas that are landscaped, planted, and maintained (including athletic fields). If less than 5 acres, data not necessary.', null=True, verbose_name=b'Acres of cultivated grounds', blank=True)),
                ('undeveloped_land_acres', models.FloatField(help_text=b'Areas without any buildings or development. If less than 5 acres, data not necessary', null=True, verbose_name=b'Acres of undeveloped land', blank=True)),
                ('ag_school_present', models.NullBooleanField(verbose_name=b'Agricultural school is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('ag_school_included', models.NullBooleanField(verbose_name=b'Agricultural school is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('ag_school_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('med_school_present', models.NullBooleanField(verbose_name=b'Medical school is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('med_school_included', models.NullBooleanField(verbose_name=b'Medical school is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('med_school_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('pharm_school_present', models.NullBooleanField(verbose_name=b'Pharmacy school is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('pharm_school_included', models.NullBooleanField(verbose_name=b'Pharmacy school is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('pharm_school_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('pub_health_school_present', models.NullBooleanField(verbose_name=b'Public health school is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('pub_health_school_included', models.NullBooleanField(verbose_name=b'Public health school is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('pub_health_school_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('vet_school_present', models.NullBooleanField(verbose_name=b'Veterinary school is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('vet_school_included', models.NullBooleanField(verbose_name=b'Veterinary school is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('vet_school_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('sat_campus_present', models.NullBooleanField(verbose_name=b'Satellite campuses are present', choices=[(True, b'Yes'), (False, b'No')])),
                ('sat_campus_included', models.NullBooleanField(verbose_name=b'Satellite campuses are included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('sat_campus_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('hospital_present', models.NullBooleanField(verbose_name=b'Hospital is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('hospital_included', models.NullBooleanField(verbose_name=b'Hospital is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('hospital_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('farm_present', models.NullBooleanField(help_text=b'Larger than 5 acres', verbose_name=b'Farm is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('farm_included', models.NullBooleanField(verbose_name=b'Farm is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('farm_acres', models.FloatField(null=True, verbose_name=b'Number of acres', blank=True)),
                ('farm_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('agr_exp_present', models.NullBooleanField(help_text=b'Larger than 5 acres', verbose_name=b'Agricultural experiment station is present', choices=[(True, b'Yes'), (False, b'No')])),
                ('agr_exp_included', models.NullBooleanField(verbose_name=b'Agricultural experiment station is included in submission', choices=[(True, b'Yes'), (False, b'No')])),
                ('agr_exp_acres', models.IntegerField(null=True, verbose_name=b'Number of acres', blank=True)),
                ('agr_exp_details', models.TextField(null=True, verbose_name=b'Reason for Exclusion', blank=True)),
                ('additional_details', models.TextField(null=True, blank=True)),
                ('climate_region', models.ForeignKey(blank=True, to='institutions.ClimateZone', help_text=b"See the <a href='http://apps1.eere.energy.gov/buildings/publications/pdfs/building_america/ba_climateguide_7_1.pdf'>USDOE</a> site and <a href='http://www.ashrae.org/File%20Library/docLib/Public/20081111_cztables.pdf'>ASHRAE</a>  (international) for more information.", null=True)),
            ],
            options={
                'verbose_name_plural': 'Boundaries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategorySubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField(null=True, blank=True)),
                ('category', models.ForeignKey(to='credits.Category')),
            ],
            options={
                'ordering': ('category__ordinal',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChoiceSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreditSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('available_point_cache', models.FloatField(null=True, blank=True)),
                ('is_unlocked_for_review', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('credit__type', 'credit__ordinal'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreditSubmissionInquiry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('explanation', models.TextField()),
                ('credit', models.ForeignKey(to='credits.Credit')),
            ],
            options={
                'verbose_name_plural': 'Credit Submission Inquiries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreditSubmissionReviewNotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.CharField(max_length=b'32', choices=[(b'best-practice', b'Best Practice'), (b'revision-request', b'Revision Request'), (b'suggestion-for-improvement', b'Suggestion For Improvement')])),
                ('comment', models.TextField(null=True, blank=True)),
                ('send_email', models.BooleanField(default=True)),
                ('email_sent', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('kind', 'credit_user_submission__credit__identifier', 'id'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreditTestSubmission',
            fields=[
                ('creditsubmission_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='submissions.CreditSubmission')),
                ('expected_value', models.FloatField(help_text=b'Point value expected from the formula for this test data', null=True, blank=True)),
            ],
            options={
            },
            bases=('submissions.creditsubmission',),
        ),
        migrations.CreateModel(
            name='CreditUserSubmission',
            fields=[
                ('creditsubmission_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='submissions.CreditSubmission')),
                ('assessed_points', models.FloatField(null=True, blank=True)),
                ('last_updated', models.DateTimeField(null=True, blank=True)),
                ('submission_status', models.CharField(default=b'ns', max_length=8, choices=[(b'c', b'Complete'), (b'p', b'In Progress'), (b'np', b'Not Pursuing'), (b'na', b'Not Applicable'), (b'ns', b'Not Started')])),
                ('internal_notes', models.TextField(help_text=b'This field is useful if you want to store notes for other people in your organization regarding this credit. They will not be published.', null=True, blank=True)),
                ('submission_notes', models.TextField(help_text=b'Use this space to add any additional information you may have about this credit. This will be published along with your submission.', null=True, blank=True)),
                ('responsible_party_confirm', models.BooleanField(default=False)),
                ('review_conclusion', models.CharField(default=b'not-reviewed', max_length=32, choices=[(b'not-reviewed', b'Not Reviewed'), (b'meets-criteria', b'Meets Criteria'), (b'does-not-meet-criteria', b'Does Not Meet Criteria'), (b'not-really-pursuing', b'Not Really Pursuing')])),
                ('applicability_reason', models.ForeignKey(blank=True, to='credits.ApplicabilityReason', null=True)),
            ],
            options={
            },
            bases=('submissions.creditsubmission',),
        ),
        migrations.CreateModel(
            name='DataCorrectionRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField()),
                ('new_value', models.TextField(help_text=b"Note: if this is a numeric field, be sure to use the institution's preference for metric/imperial. You can find this in their settings.")),
                ('explanation', models.TextField()),
                ('approved', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DateSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.DateField(null=True, blank=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='datesubmission_set', to='credits.DocumentationField')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtensionRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_deadline', models.DateField()),
                ('date', models.DateField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('description', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LongTextSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='longtextsubmission_set', to='credits.DocumentationField')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultiChoiceSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='multichoicesubmission_set', to='credits.DocumentationField')),
                ('value', models.ManyToManyField(to='credits.Choice', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NumericSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(null=True, blank=True)),
                ('metric_value', models.FloatField(null=True, blank=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='numericsubmission_set', to='credits.DocumentationField')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('reason', models.CharField(max_length=b'16', choices=[(b'member_reg', b'member_reg'), (b'nonmember_reg', b'nonmember_reg'), (b'member_renew', b'member_renew'), (b'nonmember_renew', b'nonmember_renew'), (b'international', b'international')])),
                ('type', models.CharField(max_length=b'8', choices=[(b'credit', b'credit'), (b'check', b'check'), (b'later', b'pay later')])),
                ('confirmation', models.CharField(help_text=b'The CC confirmation code or check number', max_length=b'16', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportingFieldDataCorrection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('previous_value', models.TextField()),
                ('change_date', models.DateField()),
                ('object_id', models.PositiveIntegerField()),
                ('explanation', models.TextField(null=True, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('request', models.OneToOneField(related_name='applied_correction', null=True, blank=True, to='submissions.DataCorrectionRequest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResponsibleParty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('title', models.CharField(max_length=128)),
                ('department', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=75)),
                ('phone', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('institution', models.ForeignKey(to='institutions.Institution')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
                'verbose_name_plural': 'Responsible Parties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubcategoryQuartiles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('institution_type', models.CharField(default=b'', max_length=128)),
                ('first', models.FloatField(default=0)),
                ('second', models.FloatField(default=0)),
                ('third', models.FloatField(default=0)),
                ('fourth', models.FloatField(default=0)),
                ('subcategory', models.ForeignKey(to='credits.Subcategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubcategorySubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('points', models.FloatField(null=True, blank=True)),
                ('percentage_score', models.FloatField(default=0.0, null=True, blank=True)),
                ('adjusted_available_points', models.FloatField(default=0.0, null=True, blank=True)),
                ('category_submission', models.ForeignKey(to='submissions.CategorySubmission')),
                ('subcategory', models.ForeignKey(to='credits.Subcategory')),
            ],
            options={
                'ordering': ('subcategory__ordinal',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionInquiry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('anonymous', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=128, null=True, blank=True)),
                ('last_name', models.CharField(max_length=128, null=True, blank=True)),
                ('affiliation', models.CharField(max_length=128, null=True, blank=True)),
                ('city', models.CharField(max_length=32, null=True, blank=True)),
                ('state', models.CharField(max_length=2, null=True, blank=True)),
                ('email_address', models.EmailField(max_length=75, null=True, blank=True)),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20, null=True, blank=True)),
                ('additional_comments', models.TextField(help_text=b'Include any other comments about the Submission, including the Submission Boundary and Subcategory Descriptions.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Submission Inquiries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_registered', models.DateField()),
                ('date_published', models.DateField(null=True, blank=True)),
                ('date_reviewed', models.DateField(null=True, blank=True)),
                ('date_submitted', models.DateField(null=True, blank=True)),
                ('expired', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=8, choices=[(b'ps', b'Pending Submission'), (b'pr', b'Processing Submission'), (b'rv', b'Review Submission'), (b'r', b'Rated'), (b'f', b'Finalized')])),
                ('submission_boundary', models.TextField(help_text=b"The following is an example institutional boundary: This submission includes all of the the University's main campus as well as the downtown satellite campus. The University hospital and campus farm are excluded.", null=True, blank=True)),
                ('presidents_letter', models.FileField(upload_to=stars.apps.submissions.models.upload_path_callback, max_length=255, blank=True, help_text=b"Please upload a letter from your institution's president, chancellor or other high ranking executive in PDF format.", null=True, verbose_name=b'Executive Letter')),
                ('reporter_status', models.BooleanField(default=False, help_text=b'Check this box if you would like to be given reporter status and not receive a STARS rating from AASHE.')),
                ('pdf_report', models.FileField(max_length=255, null=True, upload_to=stars.apps.submissions.models.upload_path_callback, blank=True)),
                ('is_locked', models.BooleanField(default=False)),
                ('is_visible', models.BooleanField(default=True, help_text=b'Is this submission visible to the institution? Often used with migrations.')),
                ('score', models.FloatField(null=True, blank=True)),
                ('date_created', models.DateField(auto_now_add=True, null=True)),
                ('creditset', models.ForeignKey(to='credits.CreditSet')),
                ('institution', models.ForeignKey(to='institutions.Institution')),
                ('migrated_from', models.ForeignKey(related_name='+', blank=True, to='submissions.SubmissionSet', null=True)),
                ('rating', models.ForeignKey(blank=True, to='credits.Rating', null=True)),
                ('registering_user', models.ForeignKey(related_name='registered_submissions', to=settings.AUTH_USER_MODEL)),
                ('submitting_user', models.ForeignKey(related_name='submitted_submissions', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('date_registered',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255, null=True, blank=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='textsubmission_set', to='credits.DocumentationField')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UploadSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FileField(max_length=255, null=True, upload_to=stars.apps.submissions.models.upload_path_callback, blank=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='uploadsubmission_set', to='credits.DocumentationField')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='URLSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.URLField(null=True, blank=True)),
                ('credit_submission', models.ForeignKey(to='submissions.CreditSubmission')),
                ('documentation_field', models.ForeignKey(related_name='urlsubmission_set', to='credits.DocumentationField')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='urlsubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='uploadsubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='textsubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.AddField(
            model_name='submissioninquiry',
            name='submissionset',
            field=models.ForeignKey(to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='subcategorysubmission',
            unique_together=set([('category_submission', 'subcategory')]),
        ),
        migrations.AlterUniqueTogether(
            name='subcategoryquartiles',
            unique_together=set([('subcategory', 'institution_type')]),
        ),
        migrations.AddField(
            model_name='payment',
            name='submissionset',
            field=models.ForeignKey(to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='numericsubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='longtextsubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.AddField(
            model_name='extensionrequest',
            name='submissionset',
            field=models.ForeignKey(to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extensionrequest',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='datesubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.AddField(
            model_name='creditusersubmission',
            name='responsible_party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='submissions.ResponsibleParty', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creditusersubmission',
            name='subcategory_submission',
            field=models.ForeignKey(to='submissions.SubcategorySubmission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creditusersubmission',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creditsubmissionreviewnotation',
            name='credit_user_submission',
            field=models.ForeignKey(to='submissions.CreditUserSubmission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creditsubmissioninquiry',
            name='submission_inquiry',
            field=models.ForeignKey(to='submissions.SubmissionInquiry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creditsubmission',
            name='credit',
            field=models.ForeignKey(to='credits.Credit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choicesubmission',
            name='credit_submission',
            field=models.ForeignKey(to='submissions.CreditSubmission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choicesubmission',
            name='documentation_field',
            field=models.ForeignKey(related_name='choicesubmission_set', to='credits.DocumentationField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choicesubmission',
            name='value',
            field=models.ForeignKey(blank=True, to='credits.Choice', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='categorysubmission',
            name='submissionset',
            field=models.ForeignKey(to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='categorysubmission',
            unique_together=set([('submissionset', 'category')]),
        ),
        migrations.AddField(
            model_name='boundary',
            name='submissionset',
            field=models.OneToOneField(to='submissions.SubmissionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='booleansubmission',
            name='credit_submission',
            field=models.ForeignKey(to='submissions.CreditSubmission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='booleansubmission',
            name='documentation_field',
            field=models.ForeignKey(related_name='booleansubmission_set', to='credits.DocumentationField'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='booleansubmission',
            unique_together=set([('documentation_field', 'credit_submission')]),
        ),
        migrations.CreateModel(
            name='ChoiceWithOtherSubmission',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('submissions.choicesubmission', stars.apps.submissions.models.AbstractChoiceWithOther),
        ),
        migrations.CreateModel(
            name='MultiChoiceWithOtherSubmission',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('submissions.multichoicesubmission', stars.apps.submissions.models.AbstractChoiceWithOther),
        ),
    ]
