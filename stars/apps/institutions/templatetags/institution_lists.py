from os.path import basename
from datetime import date
from django import template
from django.conf import settings
from django.db.models import Q

register = template.Library()

from stars.apps.submissions.models import SubmissionSet, Rating
from stars.apps.institutions.models import Institution

@register.inclusion_tag('institutions/tags/latest_registrants.html')
def show_latest_registrants(count='5'):
    """ Display the (count) most recently registered institutions """

    inst_list = Institution.objects.filter(is_participant=True).filter(current_subscription__isnull=False).order_by("-current_subscription__start_date").distinct()[:count]

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
    i_qs = Institution.objects.filter(enabled=True).filter(Q(is_participant=True) | Q(current_rating__isnull=False)).order_by('name')
    ratings = {}
    for r in Rating.objects.all():
        if r.name not in ratings.keys():
            ratings[r.name] = 0

    for i in i_qs:
        d = {
                'institution': i.profile,
                'current_rating': i.current_rating,
                'rated_submission': i.rated_submission,
                'subscription': i.current_subscription
            }
        if i.charter_participant:
            d['image_path'] = "/media/static/images/seals/STARS-Seal-CharterParticipant_70x70.png"
        else:
            d['image_path'] = "/media/static/images/seals/STARS-Seal-Participant_70x70.png"
        i_list.append(d)

    return {'mapped_institutions': i_list, 'STATIC_URL': settings.STATIC_URL}
