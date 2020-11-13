"""A report of Institutions that are sharing data with Sierra that maybe
forgot to cut a snapshot after submitting.

Output is in org-mode format.

THERE'S A HARD-CODED DATE DOWN THERE!
"""
import datetime

from stars.apps.third_parties.models import SubmissionSet, ThirdParty


def print_forgetters():

    sierra = ThirdParty.objects.get(name="Sierra Club")

    print "|Institution| Rated Submission Date| Snapshot(s)|"
    print "|-"

    for inst in sierra.get_snapshot_institutions():
        latest_rated = inst.get_latest_rated_submission()

        if (latest_rated is None or
            latest_rated.date_submitted < datetime.date(2015, 12, 01)):
            continue

        print "|", inst.name, "|", latest_rated.date_submitted, "|",

        snapshots = SubmissionSet.objects.filter(
            institution=inst,
            date_submitted__gte=latest_rated.date_submitted,
            status="f").order_by("-date_submitted")

        for snap in snapshots:
            print snap.date_submitted,
        print "|"


if __name__ == "__main__":
    print_forgetters()
