"""
    Breaking out scoring logic

    - calculate score for a specific submission/cat/sub/credit
        - update
        -
    - compare submission scores
    - update specific scores
"""

"""
    2.0 scoring map:
        SubmissionSet.get_STARS_score(recalculate=False)
        SubmissionSet.get_STARS_v2_0_score(recalculate=False)
        CategorySubmission.cat.get_score_ratio(recalculate=False)
        SubcategorySubmission.get_claimed_points(recalculate=False)
            > CreditUserSubmission.assessed_points
            ... should be ... _calculate_points
        SubcategorySubmission.get_adjusted_available_points(recalculate=False)
            > CreditUserSubmission.get_adjusted_available_points()
"""
from tabulate import tabulate


class Score():
    """
        This object reflects the overall score for a SubmissionSet

        Things it does:
            compare two submissions

    """
    def __init__(self, ss, name, id, score, children=[]):
        self.ss = ss
        self.name = name
        self.id = id
        self.score = score
        self.children = children


def get_score_obj(ss, credits=True):
    "get an object representation of a score for a submission set"
    cat_list = []
    for cat in ss.categorysubmission_set.all():
        subcat_list = []
        for sub in cat.subcategorysubmission_set.all():
            subcat_score = Score(
                unicode(ss), unicode(sub), sub.id, sub.get_claimed_points())
            if credits:
                credit_list = []
                for credit in sub.creditusersubmission_set.all():
                    credit_list.append(
                        Score(
                            unicode(ss), unicode(credit),
                            credit.id, credit.assessed_points))
                subcat_score.children = credit_list
            subcat_list.append(subcat_score)

        cat_list.append(Score(
            unicode(ss), unicode(cat), cat.id,
            cat.get_score_ratio()[0], subcat_list))
    return Score(unicode(ss), unicode(ss), ss.id, ss.get_STARS_score(), cat_list)


def compare_score_objects(s1, s2, display_table):
    if s1.name != s2.name:
        assert False
    if abs(s1.score - s2.score) > .1:
        display_table.append([
            s1.ss, s1.name, s1.id, s1.score, s2.score, abs(s1.score - s2.score)
        ])
        # print "[%.2f %.2f] %s" % (s1.score, s2.score, s1.name)
    for i in range(len(s1.children)):
        compare_score_objects(s1.children[i], s2.children[i], display_table)


def recalculate_all_scores(ss):
    "recalculate a submission set's score all the way down to credits"
    for cat in ss.categorysubmission_set.all():
        for sub in cat.subcategorysubmission_set.all():
            for c in sub.creditusersubmission_set.all():
                c.save()
            sub.get_adjusted_available_points(recalculate=True)
            sub.get_claimed_points(recalculate=True)
        cat.get_score_ratio(recalculate=True)
    ss.get_STARS_score(recalculate=True)
