from django import template
from django.conf import settings

register = template.Library()

from stars.apps.submissions.models import SubmissionSet, Rating
from stars.apps.institutions.models import Institution


@register.inclusion_tag('institutions/tags/latest_registrants.html')
def show_latest_registrants(count='5'):
    """ Display the (count) most recently registered institutions """

    inst_list = Institution.objects.filter(is_participant=True).filter(
        current_subscription__isnull=False).order_by("-current_subscription__start_date").distinct()[:count]

#    query_set = SubmissionSet.objects.published().order_by('-date_registered').select_related("institution")
#
#    inst_list = []
#    for s in query_set[0:count]:
#        inst_list.append(s.institution)

    return {'inst_list': inst_list}


@register.inclusion_tag('institutions/tags/rated_list.html')
def show_rated_registrants(count='5'):
    """ Display the (count) most recently registered institutions """

    query_set = SubmissionSet.objects.get_rated().order_by(
        '-date_submitted').select_related("institution")

    return {'ss_list': query_set[0:count], 'STATIC_URL': settings.STATIC_URL}


@register.inclusion_tag('institutions/tags/participant_map.html')
def show_institutions_map():
    """ Displays a map of institution participating in STARS """

    i_list = []
    i_qs = (Institution.objects.filter(enabled=True)
            .select_related(
            'ms_institution',
            'current_rating',
            'rated_submission',
            )
            )

    for i in i_qs:

        d = {
            'institution': i.ms_institution,
            'current_rating': i.current_rating,
            'rated_submission': i.rated_submission,
            'subscription': i.access_level == "Full"
        }

        if i.current_rating:
            d['image_large'] = i.current_rating.image_large
            d['map_icon'] = i.current_rating.map_icon.url

        if i.current_subscription:
            d['image_path'] = "https://reports.aashe.org/media/static/images/seals/Stars_Seal_Participant_RGB_300.png"
            d['image_title'] = "Current STARS Participant"
        i_list.append(d)

    return {'mapped_institutions': i_list, 'STATIC_URL': settings.STATIC_URL}
