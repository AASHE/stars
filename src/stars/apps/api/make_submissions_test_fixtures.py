"""
    Make test fixtures for API tests.
"""
from django.core import serializers

import stars.apps.submissions.newapi.resources as submissions_resource_models
from stars.apps.api.test import get_random_visible_resource

institutions = set()
ratings = set()
users = set()
submission_sets = set()
category_submissions = set()
subcategory_submissions = set()
credit_submissions = set()
documentation_field_submissions = list()


def fill_buckets(submission_set=None):
    submission_set = submission_set or get_random_visible_resource(
        submissions_resource_models.SubmissionSetResource)
    if submission_set in submission_sets:
        return
    if submission_set.reporter_status is None:  # Will fail validation on load.
        return
    submission_sets.add(submission_set)
    institutions.add(submission_set.institution)
    for user in (submission_set.registering_user,
                 submission_set.submitting_user):
        if user:
            users.add(user)
    if submission_set.rating:
        ratings.add(submission_set.rating)
    category_submissions.update(submission_set.categorysubmission_set.all())
    for category_submission in submission_set.categorysubmission_set.all():
        subcategory_submission = \
          category_submission.subcategorysubmission_set.all()[0]
        subcategory_submissions.add(subcategory_submission)
        for credit_submission in \
          subcategory_submission.creditusersubmission_set.all():  # noqa
            credit_submissions.add(credit_submission)
            for field in credit_submission.get_submission_fields():
                documentation_field_submissions.append(field)


def get_dump_filename(model_name):
    return 'test_api_{0}.json'.format(model_name)


def dump_buckets():
    dump_bucket(bucket=institutions, model_name='institution')
    dump_bucket(bucket=users, model_name='user')
    dump_bucket(bucket=ratings, model_name='rating')
    dump_bucket(bucket=submission_sets, model_name='submissionset')
    dump_bucket(bucket=category_submissions, model_name='categorysubmission')
    dump_bucket(bucket=subcategory_submissions,
                model_name='subcategorysubmission')
    dump_bucket(bucket=credit_submissions, model_name='creditsubmission')
    dump_bucket(bucket=documentation_field_submissions,
                model_name='documentationfieldsubmission')


def dump_bucket(bucket, model_name):
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()

    file_name = get_dump_filename(model_name)
    with open(file_name, 'w') as fixture:
        json_serializer.serialize(bucket, stream=fixture, indent=4)
