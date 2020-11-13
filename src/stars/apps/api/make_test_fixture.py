"""
    Make test fixtures for API tests.
"""
from django.core import serializers

import stars.apps.api.make_submissions_test_fixtures as submissions_fixtures
import stars.apps.credits.api.resources as credits_resource_models
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.newapi.resources import SubmissionSetResource
from stars.apps.api.test import get_random_visible_resource

CREDITS_TO_DUMP = 5

creditsets = set()
categories = set()
subcategories = set()
credits = set()
documentation_fields = list()


def fill_buckets():

    while len(credits) < CREDITS_TO_DUMP:
        credit = get_random_visible_resource(
            credits_resource_models.CreditResource)
        credits.add(credit)
        fill_buckets_for_credit(credit)

    # Add one non-visible SubmissionSet:
    for submissionset in SubmissionSet.objects.all():
        if submissionset not in SubmissionSetResource._meta.queryset:
            submissions_fixtures.fill_buckets(submissionset)
            break


def fill_buckets_for_credit(credit):
    global documentation_fields
    documentation_fields += credit.documentationfield_set.all()
    subcategories.add(credit.subcategory)
    categories.add(credit.subcategory.category)
    creditset = credit.subcategory.category.creditset
    creditsets.add(creditset)
    for submissionset in creditset.submissionset_set.all()[:2]:
        submissions_fixtures.fill_buckets(submissionset)


def get_dump_filename(model_name):
    return 'test_api_{0}.json'.format(model_name)


def dump_buckets():
    dump_bucket(bucket=creditsets, model_name='creditset')
    dump_bucket(bucket=categories, model_name='category')
    dump_bucket(bucket=subcategories, model_name='subcategory')
    dump_bucket(bucket=credits, model_name='credit')
    dump_bucket(bucket=documentation_fields, model_name='documentationfield')
    submissions_fixtures.dump_buckets()


def dump_bucket(bucket, model_name):
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()

    file_name = get_dump_filename(model_name)
    with open(file_name, 'w') as fixture:
        json_serializer.serialize(bucket, stream=fixture, indent=4)
