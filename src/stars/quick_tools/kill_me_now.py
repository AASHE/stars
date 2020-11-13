import datetime
import pickle

from stars.apps.institutions.management.commands import restore_institution
from stars.apps.submissions.models import CreditUserSubmission


def check_match(left, right):

    if left["cus"].credit.title != right["cus"].credit.title:
        return (False, "credit.title values differ (left: {left_credit_title}, "
                "right: {right_credit_title}".format(
                    left_credit_title=left["cus"].credit.title,
                    right_credit_title=right["cus"].credit.title))
    elif (left["cus"].subcategory_submission.subcategory.title !=
          right["cus"].subcategory_submission.subcategory.title):
        return (False, "subcategory_submission.subcategory.title values differ "
                "(left: {left_credit_title}, right: {right_credit_title}".format(
                    left_credit_title=left["cus"].subcategory_submission.subcategory.title,
                    right_credit_title=right["cus"].subcategory_submission.subcategory.title))
    elif (left["cus"].subcategory_submission.category_submission.category.title !=
          right["cus"].subcategory_submission.category_submission.category.title):
        return (False, "subcategory_submission.category_submission.category.title "
                "values differ (left: {left_category_title}, "
                "right: {right_category_title}".format(
                    left_category_title=left["cus"].subcategory_submission.category_submission.category.title,
                    right_category_title=right["cus"].subcategory_submission.category_submission.category.title))
    else:
        if left["submissionset"].pk != right["submissionset"].pk:
            return (False, "submissionset.pk values differ, left: {left_pk}, "
                    "right: {right_pk}".format(left_pk=left["submissionset"].pk,
                                               right_pk=right["submissionset"].pk))
        elif (left["submissionset"].institution.name !=
              right["submissionset"].institution.name):
            return (False, "submissionset.institution.name values differ, "
                    "left: {left_name}, right: {right_name}".format(
                        left_name=left["submissionset"].institution.name,
                        right_name=right["submissionset"].institution.name))
        else:
            return (True, None)


matched = []
unmatched = []
updated = []
live_is_more_recent = []
exceptions = []


def update_all_credit_user_submissions():

    global matched, unmatched, updated, live_is_more_recent, exceptions

    for cus in CreditUserSubmission.objects.using("stars-backup").filter(
            last_updated__gt=datetime.date(2019, 04, 01)):

        try:
            live_match = CreditUserSubmission.objects.using("default").get(
                pk=cus.pk)
        except CreditUserSubmission.DoesNotExist:
            unmatched.append({"cus": cus,
                              "submissionset": cus.get_submissionset(),
                              "error_message": "no match on CreditUserSubmission.pk"})
        else:
            cus_submissionset = cus.get_submissionset()
            match_submissionset = live_match.get_submissionset()
            matches, error_message = check_match(
                {"cus": cus, "submissionset": cus.get_submissionset()},
                {"cus": live_match, "submissionset": match_submissionset})
            if matches:
                matched.append({"cus": cus,
                                "submissionset": cus_submissionset})
                if live_match.last_updated < cus.last_updated:
                    try:
                        restore_institution.restore_credit_user_submission(
                            credit_user_submission=cus,
                            source_db="stars-backup",
                            target_db="default")
                    except Exception as exc:
                        print live_match.pk, " not updated:", exc
                        exceptions.append({"cus": live_match,
                                           "submissionset": match_submissionset,
                                           "exception": exc})
                    else:
                        updated.append({"cus": live_match,
                                        "submissionset": match_submissionset})
                else:
                    live_is_more_recent.append({"cus": live_match,
                                                "submissionset": match_submissionset})
            else:
                print cus.pk, "check_match error:", error_message
                unmatched.append({"cus": cus,
                                  "submissionset": cus_submissionset,
                                  "error_message": error_message})

def recalculate_submissions():
    for submissionset in set([cus["submissionset"] for cus in updated]):
        print "recalculating", submissionset,
        print " was", submissionset.get_STARS_score(),
        print " now", submissionset.get_STARS_score(recalculate=True)


def report():

    # reports_url = "http://localhost:8000"
    reports_url = "https://reports.aashe.org"

    def dressed_manage_url(submissionset):
        return reports_url + submissionset.get_manage_url()

    def dressed_scorecard_url(credit_user_submission):
        return reports_url + credit_user_submission.get_scorecard_url()

    def dressed_submit_url(credit_user_submission):
        return reports_url + credit_user_submission.get_submit_url()

    print("matched: ", len(matched))
    print("unmatched: ", len(unmatched))
    print("updated:", len(updated))
    print("live_is_more_recent:", len(live_is_more_recent))
    print("exceptions:", len(exceptions))
    print
    print
    print("updated submissionsets:")
    print
    for submissionset in sorted(
            set([cus["submissionset"] for cus in updated]),
            key=lambda k: k.institution.name):
        print "* updated:", submissionset, '(' + str(submissionset.pk) + ')'
        print "          ", dressed_manage_url(submissionset=submissionset)
        for cus in [
                cus for cus in updated if cus["submissionset"] == submissionset]:
            print "           credit:", cus["cus"].credit
            print "                  ", dressed_scorecard_url(cus["cus"])
            print "                  ", dressed_submit_url(cus["cus"])
        print

    print("live is newer submissionsets:")
    print
    for submissionset in sorted(
            set([cus["cus"].get_submissionset() for cus in live_is_more_recent]),
            key=lambda k: k.institution.name):
        print "* live is newer:", submissionset, '(' + str(submissionset.pk) + ')'
        print "                ", dressed_manage_url(submissionset=submissionset)
        for cus in [
                cus for cus in live_is_more_recent if cus["submissionset"] == submissionset]:
            print "           credit:", cus["cus"].credit
            print "                  ", dressed_scorecard_url(cus["cus"])
            print "                  ", dressed_submit_url(cus["cus"])
        print

    print("unmatched submissionsets:")
    print
    for submissionset in sorted(
            set([cus["cus"].get_submissionset() for cus in unmatched]),
            key=lambda k: k.institution.name):
        print "* unmatched:", submissionset, '(' + str(submissionset.pk) + ')'
        print "            ", dressed_manage_url(submissionset=submissionset)
        for cus in [
                cus for cus in unmatched if cus["submissionset"] == submissionset]:
            print "           credit:", cus["cus"].credit
            print "                  ", cus["error_message"]
            print "                  ", dressed_scorecard_url(cus["cus"])
            print "                  ", dressed_submit_url(cus["cus"])
        print

    print("exceptions:")
    print
    for submissionset in sorted(
            set([cus["cus"].get_submissionset() for cus in exceptions]),
            key=lambda k: k.institution.name):
        print "* exception:", submissionset, '(' + str(submissionset.pk) + ')'
        print "            ", dressed_manage_url(submissionset=submissionset)
        for cus in [
                cus for cus in exceptions if cus["submissionset"] == submissionset]:
            print "           credit:", cus["cus"].credit
            print "                  ", dressed_scorecard_url(cus["cus"])
            print "                   ", dressed_submit_url(cus["cus"])
            print "                  ", cus["exception"]
        print

def handle_unmatched():

    import ipdb; ipdb.set_trace()

    for nomatch in unmatched:
        # No CreditUserSubmission with same pk.  How can that
        # happen?  Shouldn't all CreditUserSubmissions extant
        # on 4/4/2019 still be in the live system?
        print nomatch
