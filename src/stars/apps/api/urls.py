from tastypie.api import Api
import stars.apps.credits.api.resources as credits_resources
import stars.apps.submissions.newapi.resources as submissions_resources
import stars.apps.institutions.api.resources as institutions_resources
import stars.apps.helpers.api.resources as helpers_resources


api = Api(api_name='0.1')


for resource in (credits_resources.CategoryResource,
                 credits_resources.CreditResource,
                 credits_resources.CreditSetResource,
                 credits_resources.DocumentationFieldResource,
                 credits_resources.SubcategoryResource):
    api.register(resource())

for resource in (submissions_resources.SubmissionSetResource,
                 submissions_resources.CategorySubmissionResource,
                 submissions_resources.SubcategorySubmissionResource,
                 submissions_resources.CreditSubmissionResource):
    api.register(resource())

api.register(institutions_resources.InstitutionResource())

api.register(helpers_resources.BlockContentResource())

app_name = 'api'

urlpatterns = api.urls
