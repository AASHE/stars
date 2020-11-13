from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from stars.apps.submissions.models import NumericSubmission


class Command(BaseCommand):
    help = """
        Runs report on fault state of Numeric Submission.

        Ideally, NumericSubmissions should have the same value for
        metric and imperial.
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        qs = NumericSubmission.objects.filter(
            documentation_field__units__isnull=True)

        print("Total NumericSubmissions with no units: %d" % qs.count())

        # qs = qs.filter(
        #     documentation_field__title__contains="percentage")
        # print("Of those, %d, say 'percentage' in the title" % qs.count())

        print("""
        Each of these should have the same imperial and metric values,
        or the metric value should be None.
        """)

        fault_count = 0
        faulty_reports = []
        qs = qs.filter(value__isnull=False)
        for ns in qs:
            if ns.value != ns.metric_value and ns.metric_value != None:
                # print("%s\t\t\t%s" % (ns.value, ns.metric_value))
                fault_count += 1
                ss = ns.credit_submission.creditusersubmission.subcategory_submission.category_submission.submissionset
                if ss not in faulty_reports:
                    faulty_reports.append(ss)

        print("\n%d (%.2f%%) fields fail that" % (
            fault_count, (100.0 * fault_count / qs.count())))

        print("\nin %d reports\n\n" % len(faulty_reports))
        for ss in faulty_reports:
            print(ss)
