import collections
import functools

from stars.apps.submissions.models import (RATED_SUBMISSION_STATUS,
                                           SubmissionSet)

"""
Ben's psuedocode:

previousSubmissionGroup = Rated submissions and MigratedFromSubmission

for each documentationFieldSubmission in currentSubmissionSet:
	for each previousSubmissionSet in previousSubmissionGroup:
		follow documentationFieldSubmission.documentation_field.previous_version tree to an olddocumentationfield that is in previousSubmissionSet.creditset
		find oldDocumentationFieldSubmission with previousSubmissionSet as parent and olddocumentationfield as documentation_field:
			print oldDocumentationField value
"""

def get_submissionsets_to_include_in_history(institution):
    """Returns the list of SubmissionSets for `institution` that
    should be included in CreditUserSubmission history reports.

    SubmissionSets are provided as a list of named tuples, consisting
    of a SubmissionSet and an explaination of the historical
    significance of them.  E.g., "this one was submitted on April 1,"
    and "this one was migrated."

    SubmissionSets are included if 

      1. they're rated, or 

      2. they were migrated to a new SubmissionSet.
    """
    HistoricalSubmissionSet = collections.namedtuple(
        'HistoricalSubmissionSet',
        ['submissionset', 'historical_significance'])
    submissionsets = []
    for submissionset in SubmissionSet.objects.filter(
            institution=institution):
        if submissionset.migrated_from:
            submissionsets.append(
                HistoricalSubmissionSet(
                    submissionset.migrated_from,
                    "migrated on {date}".format(
                        date=submissionset.date_created.isoformat())))
        if submissionset.status == RATED_SUBMISSION_STATUS:
            submissionsets.append(
                HistoricalSubmissionSet(
                    submissionset,
                    "submitted on {date}".format(
                        date=submissionset.date_submitted.isoformat())))
    return submissionsets

def get_all_doc_field_versions(doc_field):
    """Returns all versions of a DocumentationField in a 
    dictionary keyed by CreditSet.
    """
    versions = {}
    for version in doc_field.get_all_versions():
        versions[version.get_creditset()] = version
    return versions

# memoize from https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize:
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

@memoize
def get_all_doc_field_subs_in_submissionset(submissionset):
    """Returns all DocumentationFieldSubmissions for `submissionset`
    as a dictionary keyed by related DocumentationFields.
    """
    doc_field_subs = {}
    
    for cat_sub in submissionset.categorysubmission_set.all():
        for subcat_sub in cat_sub.subcategorysubmission_set.all():
            for credituser_sub in subcat_sub.creditusersubmission_set.all():
                for doc_field_sub in credituser_sub.get_submission_fields():
                    doc_field_subs[doc_field_sub.documentation_field] = (
                        doc_field_sub)
    return doc_field_subs

def get_credit_submission_history(credit_submission):
    """Returns historical DocumentationFieldSubmissions for
    `credit_submission` as a dictionary, keyed by the related
    DocumentationField.

    DocumentationFieldSubmissions (the values in the dictionary
    returned by this function) are represented by a namedtuple that
    contains the DocumentationFieldSubmission and the reason for its
    historical significance (copied from the related historical
    SubmissionSet).

    Only DocumentationFieldSubmissions in SubmissionSets that
    pass the get_submissionsets_to_include_in_history() filter
    are included.
    """
    history = collections.OrderedDict()

    HistoricalDocFieldSub = collections.namedtuple('HistoricalDocFieldSub',
                                                   ['doc_field_sub',
                                                    'historical_significance'])
    
    historical_submissionsets = get_submissionsets_to_include_in_history(
        institution=credit_submission.get_submissionset().institution)

    for doc_field_submission in credit_submission.get_submission_fields():

        # All versions of the DocumentationField for this
        # DocumentationFieldSubmission:
        all_doc_fields = get_all_doc_field_versions(
            doc_field_submission.documentation_field)
        
        if all_doc_fields:
            
            for historical_submissionset in historical_submissionsets:
                submissionset = historical_submissionset.submissionset
                # A version of the DocumentationField for this
                # DocumentationFieldSubmission in this submissionset:
                try:
                    all_doc_field = (
                        all_doc_fields[submissionset.creditset])
                except KeyError:
                    continue

                # Find DocumentationFieldSubmission in submissionset,
                # for all_doc_field:
                all_doc_field_subs_in_submissionset = (
                    get_all_doc_field_subs_in_submissionset(submissionset))

                if all_doc_field in all_doc_field_subs_in_submissionset:
                    historical_doc_field_sub = HistoricalDocFieldSub(
                        all_doc_field_subs_in_submissionset[all_doc_field],
                        historical_submissionset.historical_significance)

                    try:
                        history[
                            doc_field_submission.documentation_field].append(
                                historical_doc_field_sub)
                    except KeyError:
                        history[doc_field_submission.documentation_field] = [
                            historical_doc_field_sub]

    return history

