# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicabilityReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.CharField(max_length=128)),
                ('help_text', models.TextField(null=True, blank=True)),
                ('ordinal', models.IntegerField()),
            ],
            options={
                'ordering': ('ordinal',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('abbreviation', models.CharField(help_text=b'Typically a 2 character code for the category. e.g.,ER for Education & Research', max_length=6)),
                ('ordinal', models.SmallIntegerField(default=-1)),
                ('max_point_value', models.IntegerField(default=0)),
                ('description', models.TextField(null=True, blank=True)),
                ('include_in_report', models.BooleanField(default=True)),
                ('include_in_score', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('ordinal',),
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=255, verbose_name=b'Choice')),
                ('ordinal', models.SmallIntegerField(default=-1)),
                ('is_bonafide', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('ordinal',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('ordinal', models.SmallIntegerField(default=-1, help_text=b'The order of this credit within sub-category.', db_index=True)),
                ('number', models.SmallIntegerField(default=-1, help_text=b'The number of this credit within the main category. EX: "ER Credit 1"')),
                ('point_value', models.FloatField(help_text=b'The maximum points awarded for this credit.')),
                ('point_minimum', models.FloatField(help_text=b'If not blank, then this is the minimum value in the max available point range.', null=True, blank=True)),
                ('point_variation_reason', models.TextField(help_text=b'An explanation of why the available points vary for this credit', null=True, blank=True)),
                ('point_value_formula', models.TextField(help_text=b'Formula to compute the maximum available points for a credit', null=True, verbose_name=b'Max point value formula', blank=True)),
                ('formula', models.TextField(default=b'points = 0', help_text=b'Formula to compute credit points from values of the reporting fields', null=True, verbose_name=b'Points Calculation Formula', blank=True)),
                ('validation_rules', models.TextField(help_text=b'A Python script that provides custom validation for this credit.', null=True, verbose_name=b'Custom Validation', blank=True)),
                ('type', models.CharField(db_index=True, max_length=2, choices=[(b't1', b'Tier 1'), (b't2', b'Tier 2')])),
                ('criteria', models.TextField()),
                ('applicability', models.TextField(null=True, blank=True)),
                ('scoring', models.TextField()),
                ('measurement', models.TextField(null=True, blank=True)),
                ('staff_notes', models.TextField(null=True, verbose_name=b'AASHE Staff Notes', blank=True)),
                ('identifier', models.CharField(default=b'ID?', max_length=16, db_index=True)),
                ('show_info', models.BooleanField(default=True, help_text=b"Indicates if this credit will have the 'info' tab")),
                ('is_required', models.BooleanField(default=False, help_text=b'Must this credit be completed before submitting for a rating?')),
                ('is_opt_in', models.BooleanField(default=False, help_text=b'Is this an opt-in credit?')),
                ('resources', models.TextField(help_text=b'A list of resources related to this credit', null=True, blank=True)),
                ('previous_version', models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.Credit')),
            ],
            options={
                'ordering': ('ordinal',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreditSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(unique=True, max_length=5)),
                ('release_date', models.DateField()),
                ('tier_2_points', models.FloatField()),
                ('is_locked', models.BooleanField(default=False, help_text=b'When a credit set is locked, most credit editor functions will be disabled.', verbose_name=b'Lock Credits')),
                ('scoring_method', models.CharField(max_length=25, choices=[(b'get_STARS_v1_0_score', b'STARS 1.0 Scoring'), (b'get_STARS_v2_0_score', b'STARS 2.0 Scoring')])),
                ('credit_identifier', models.CharField(default=b'get_1_1_identifier', max_length=25, choices=[(b'get_1_0_identifier', b'1.0'), (b'get_1_1_identifier', b'1.1')])),
                ('previous_version', models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.CreditSet')),
            ],
            options={
                'ordering': ('release_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentationField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('header', models.TextField(default=b'', help_text=b'HTML to display before field in Reporting Tool', null=True, verbose_name=b'Header', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Promt/Question')),
                ('type', models.CharField(db_index=True, max_length=16, choices=[(b'text', b'text'), (b'long_text', b'long text'), (b'numeric', b'numeric'), (b'boolean', b'yes/no'), (b'choice', b'choose one'), (b'multichoice', b'choose many'), (b'url', b'url'), (b'date', b'date'), (b'upload', b'upload'), (b'tabular', b'tabular'), (b'calculated', b'calculated')])),
                ('last_choice_is_other', models.BooleanField(default=False, help_text=b'If selected, the last choice provides a box to enter a user-defined choice')),
                ('min_range', models.IntegerField(help_text=b'Numeric: minimum integer value, Date: earliest year.', null=True, blank=True)),
                ('max_range', models.IntegerField(help_text=b'Text: max character count, LongText: max word count, Numeric: max integer value, Date: latest year.', null=True, blank=True)),
                ('inline_help_text', models.TextField(null=True, blank=True)),
                ('tooltip_help_text', models.TextField(null=True, blank=True)),
                ('ordinal', models.SmallIntegerField(default=-1, db_index=True)),
                ('required', models.CharField(default=b'req', help_text=b'If a field is conditionally required it is important to note that in the help-text and to define a custom validation rule.', max_length=8, choices=[(b'opt', b'optional'), (b'cond', b'conditionally required'), (b'req', b'required')])),
                ('identifier', models.CharField(max_length=2, db_index=True)),
                ('is_published', models.BooleanField(default=True, help_text=b'This documentation field will be displayed in the public report. Applies to 99.99% of fields.')),
                ('tabular_fields', jsonfield.fields.JSONField(null=True, blank=True)),
                ('formula', models.TextField(default=b'', help_text=b'Formula to compute field value', null=True, verbose_name=b'Calculation Formula', blank=True)),
                ('imperial_formula_text', models.CharField(help_text=b'Imperial formula text', max_length=255, null=True, blank=True)),
                ('metric_formula_text', models.CharField(help_text=b'Metric formula text', max_length=255, null=True, blank=True)),
                ('copy_from_field', models.ForeignKey(related_name='source_field', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='credits.DocumentationField', help_text=b'Field whose value can be copied into this field.', null=True)),
                ('credit', models.ForeignKey(to='credits.Credit')),
                ('formula_terms', models.ManyToManyField(help_text=b"Fields used in this field's formula calculation.", related_name='calculated_fields', null=True, to='credits.DocumentationField', blank=True)),
                ('previous_version', models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.DocumentationField')),
            ],
            options={
                'ordering': ('ordinal',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IncrementalFeature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(unique=True)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=b'16')),
                ('minimal_score', models.SmallIntegerField(help_text=b'The minimal STARS score required to achieve this rating')),
                ('image_200', models.ImageField(help_text=b'A version of the image that fits w/in a 200x200 pixel rectangle', null=True, upload_to=b'seals', blank=True)),
                ('image_large', models.ImageField(help_text=b'A large version of the image that fits w/in a 1200x1200 pixel rectangle', null=True, upload_to=b'seals', blank=True)),
                ('map_icon', models.ImageField(null=True, upload_to=b'seals', blank=True)),
                ('publish_score', models.BooleanField(default=True)),
                ('creditset', models.ForeignKey(to='credits.CreditSet')),
            ],
            options={
                'ordering': ('-minimal_score',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=64, null=True, blank=True)),
                ('ordinal', models.SmallIntegerField(default=-1)),
                ('max_point_value', models.IntegerField(default=0)),
                ('description', models.TextField()),
                ('passthrough', models.BooleanField(default=False, help_text=b'makes the subcategory sorta invisible, for use with Inst. Characteristics')),
                ('category', models.ForeignKey(to='credits.Category')),
                ('previous_version', models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.Subcategory')),
            ],
            options={
                'ordering': ('category', 'ordinal'),
                'verbose_name_plural': 'Subcategories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('ratio', models.FloatField(default=1.0, help_text=b'Ex: 0.092903 for Square Feet because 1sqf = 0.092903sqm', null=True, blank=True)),
                ('is_metric', models.BooleanField(default=False)),
                ('equivalent', models.ForeignKey(blank=True, to='credits.Unit', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='documentationfield',
            name='units',
            field=models.ForeignKey(blank=True, to='credits.Unit', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='documentationfield',
            unique_together=set([('credit', 'identifier')]),
        ),
        migrations.AddField(
            model_name='creditset',
            name='supported_features',
            field=models.ManyToManyField(to='credits.IncrementalFeature'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='credit',
            name='subcategory',
            field=models.ForeignKey(to='credits.Subcategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choice',
            name='documentation_field',
            field=models.ForeignKey(to='credits.DocumentationField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='choice',
            name='previous_version',
            field=models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.Choice'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='creditset',
            field=models.ForeignKey(to='credits.CreditSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='previous_version',
            field=models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicabilityreason',
            name='credit',
            field=models.ForeignKey(to='credits.Credit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicabilityreason',
            name='previous_version',
            field=models.OneToOneField(related_name='_next_version', null=True, blank=True, to='credits.ApplicabilityReason'),
            preserve_default=True,
        ),
    ]
