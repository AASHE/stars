from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from stars.apps.submissions.models import SubmissionSet

OFFICIAL_URL = "https://reports.aashe.org"


class LatestReportsFeed(Feed):
    title = "Latest STARS Reports"
    link = "/institutions/participants-and-reports/"
    description = "Recently submitted STARS reports."

    def items(self):
        return SubmissionSet.objects.get_rated().order_by(
            '-date_submitted').select_related("institution")[:10]

    def item_title(self, item):
        return item.institution.name

    def item_description(self, item):
        return "%s%s" % (OFFICIAL_URL, item.rating.image_200.url)

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.get_scorecard_url()
