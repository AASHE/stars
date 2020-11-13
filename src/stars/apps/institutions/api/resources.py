"""
    STARS Institutions API
"""
from tastypie import fields

from stars.apps.institutions import models
from stars.apps.api.resources import StarsApiResource
from stars.apps.api.paths import SUBMISSIONS_RESOURCE_PATH


class InstitutionResource(StarsApiResource):
    """
        Resource for accessing any Institution.
    """
    submission_sets = fields.OneToManyField(
       SUBMISSIONS_RESOURCE_PATH + "NestedSubmissionSetResource",
       'submissionset_set', full=True)
    current_report = fields.OneToOneField(
        SUBMISSIONS_RESOURCE_PATH + "NestedSubmissionSetResource",
        'rated_submission', full=True, null=True)
    postal_code = fields.CharField(readonly=True)
    city = fields.CharField(readonly=True)
    state = fields.CharField(readonly=True)

    class Meta(StarsApiResource.Meta):
        queryset = models.Institution.objects.get_rated().order_by('name')
        resource_name = 'institutions'
        fields = ['name', 'is_member', 'country']
        allowed_methods = ['get']

    def dehydrate_city(self, bundle):
        if bundle.obj.profile:
            return bundle.obj.profile.city

    def dehydrate_state(self, bundle):
        if bundle.obj.profile:
            return bundle.obj.profile.state

    def dehydrate_postal_code(self, bundle):
        if bundle.obj.profile:
            return bundle.obj.profile.postal_code

    def dehydrate_submission_sets(self, bundle):
        """Filter unrated submission sets."""
        rated_submissions = [ss for ss in bundle.data['submission_sets']
                             if ss.obj.rating]
        return rated_submissions


class NestedInstitutionResource(StarsApiResource):
    """
        A resource for embedding institution info in other resources.
        A middle way between just an InstitutionResource URI and full=True.
    """
    class Meta(InstitutionResource.Meta):
        fields = ['name']
        allowed_methods = []
