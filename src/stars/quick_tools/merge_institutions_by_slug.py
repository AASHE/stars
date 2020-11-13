from stars.apps.institutions.models import Institution, MigrationHistory, StarsAccount
from stars.apps.submissions.models import (
                                           Rating,

                                           ResponsibleParty,
                                           SubmissionSet,
                                           Subscription)


doomed_institution_slug = raw_input("slug for doomed institution: ")
surviving_institution_slug = raw_input("slug for surviving institution: ")


doomed_institution = Institution.objects.get(slug=doomed_institution_slug)
surviving_institution = Institution.objects.get(slug=surviving_institution_slug)


# institution
surviving_institution.contact_department = doomed_institution.contact_department
surviving_institution.contact_email = doomed_institution.contact_email
surviving_institution.contact_first_name = doomed_institution.contact_first_name
surviving_institution.contact_last_name = doomed_institution.contact_last_name
surviving_institution.contact_middle_name = doomed_institution.contact_middle_name
surviving_institution.contact_title = doomed_institution.contact_title

surviving_institution.executive_contact_address = doomed_institution.executive_contact_address
surviving_institution.executive_contact_city = doomed_institution.executive_contact_city
surviving_institution.executive_contact_department = doomed_institution.executive_contact_department
surviving_institution.executive_contact_email = doomed_institution.executive_contact_email
surviving_institution.executive_contact_first_name = doomed_institution.executive_contact_first_name
surviving_institution.executive_contact_last_name = doomed_institution.executive_contact_last_name
surviving_institution.executive_contact_middle_name = doomed_institution.executive_contact_middle_name
surviving_institution.executive_contact_state = doomed_institution.executive_contact_state
surviving_institution.executive_contact_title = doomed_institution.executive_contact_title
surviving_institution.executive_contact_zip = doomed_institution.executive_contact_zip

surviving_institution.president_address = doomed_institution.president_address
surviving_institution.president_city = doomed_institution.president_city
surviving_institution.president_email = doomed_institution.president_email
surviving_institution.president_first_name = doomed_institution.president_first_name
surviving_institution.president_last_name = doomed_institution.president_last_name
surviving_institution.president_middle_name = doomed_institution.president_middle_name
surviving_institution.president_state = doomed_institution.president_state
surviving_institution.president_title = doomed_institution.president_title
surviving_institution.president_zip = doomed_institution.president_zip

surviving_institution.current_rating = doomed_institution.current_rating
surviving_institution.current_submission = doomed_institution.current_submission
surviving_institution.current_subscription = doomed_institution.current_subscription
surviving_institution.is_member = doomed_institution.is_member
surviving_institution.latest_expired_submission = doomed_institution.latest_expired_submission
surviving_institution.prefers_metric_system = doomed_institution.prefers_metric_system
surviving_institution.rated_submission = doomed_institution.rated_submission
surviving_institution.rating_expires = doomed_institution.rating_expires

surviving_institution.save()


def merge(model):
    for doomed_model in model.objects.filter(institution=doomed_institution):
        doomed_model.institution = surviving_institution
        doomed_model.save()


merge(StarsAccount)
merge(ResponsibleParty)
merge(SubmissionSet)
merge(MigrationHistory)
merge(Rating)
merge(Subscription)
