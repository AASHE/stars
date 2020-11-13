#!/usr/bin/env python
"""
    Audits the scores for all rated submissions.

    IMPORTANT:
        - Don't run on production unless you want to reevaluate all scores
        - This is very processor-heavy
"""
from django.core.management.base import BaseCommand
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import CreditSet
from ...scoring import compare_score_objects, get_score_obj

from fish import ProgressFish
from tabulate import tabulate

# encoding=utf8
import sys


class Command(BaseCommand):

    def handle(self, *args, **options):
        if len(args) == 1:
            audit_scores(args[0])
        else:
            audit_scores()


def audit_scores(ss_id=None):
    """
        recalculates all scores and display the changes
    """

    reload(sys)
    sys.setdefaultencoding('utf8')

    if not ss_id:
        print "iterating all submission sets"
        cs = CreditSet.objects.get(pk=6)
        qs = SubmissionSet.objects.filter(status='r').filter(creditset=cs)
    else:
        print "auditing SS: %s" % ss_id
        qs = [SubmissionSet.objects.get(pk=ss_id)]

    display_table = []
    fish = ProgressFish(total=len(qs))

    count = 0
    for ss in qs:
        count += 1

        fish.animate(amount=count)

        # current_score = get_score_object(ss)
        # recalculate_all_scores(ss)
        # recalculated_score = get_score_object(ss)
        # compare scores
        s1 = get_score_obj(ss, credits=False)
        ss.get_STARS_score(recalculate=True)
        s2 = get_score_obj(ss, credits=False)
        compare_score_objects(s1, s2, display_table)

    #     current_score = round(ss.score, 2)
    #     recalculated_score = round(ss.get_STARS_score(recalculate=True), 2)
    #
    #     if abs(current_score - recalculated_score) > .1:
    #         display_table.append([
    #             ss, current_score, recalculated_score,
    #             current_score - recalculated_score, ss.date_submitted, ss.id])
    #
    # if display_table:
    print tabulate(display_table, headers=[
            'submission set', 'name', 'id', 'calculated_score', 'recalculated_score',
            'delta'])
    # else:
    #     print "no discrepencies"
