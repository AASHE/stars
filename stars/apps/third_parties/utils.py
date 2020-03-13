import csv
import cStringIO
import codecs
import os

from django.core.files.temp import NamedTemporaryFile
from django.utils.encoding import smart_unicode

from stars.apps.submissions.models import (SubmissionSet,
                                           CreditUserSubmission,
                                           DocumentationFieldSubmission)


REPORTS_HOST = "reports.aashe.org"



class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def export_credit_csv(credit, ss_qs=None, outfilename=None):
    """
        Returns a NamedTemporaryFile with data from each submisisonset
        in ss_qs for the specified credit.
    """
    if not outfilename:
        outfile = NamedTemporaryFile(suffix='.csv', delete=False)
    else:
        path = os.path.dirname(outfilename)
        if not os.path.exists(path):
            os.makedirs(path)
        outfile = open(outfilename, 'wb')

    csvWriter = UnicodeWriter(outfile)

    # Get the list of submissions for columns
    if not ss_qs:
        ss_qs = SubmissionSet.objects.filter(status='r').order_by(
            "institution__name")
    ss_list = []
    cus_list = []
    for ss in ss_qs:
        ss_list.append(ss)
        try:
            cus = CreditUserSubmission.objects.get(
                credit=credit.get_for_creditset(ss.creditset),
                subcategory_submission__category_submission__submissionset=ss)
        except CreditUserSubmission.DoesNotExist:
            print "MISSING CreditUserSubmission", credit, ss
        else:
            cus_list.append(cus)

    # Get the list of fields in the credit for rows
    df_list = []
    for df in credit.documentationfield_set.all():
        df_list.append(df)

    # Create Columns

    columns = [
                u"Institution",
                u"Date Submitted",
                u"Last Updated",
                u"Liason Email",
                u"Version",
                u"Status",
               ]

    for df in df_list:
        columns.append(unicode(df))

    columns.append(u'Public Notes')

    csvWriter.writerow(columns)

    # Create Rows
    for cus in cus_list:

        institution = cus.get_institution()
        ss = cus.subcategory_submission.category_submission.submissionset

        row = [
                institution.name,
                unicode(ss.date_submitted),
                unicode(cus.last_updated),
                institution.contact_email,
                ss.creditset.version
                ]

        # Status and Score
        if cus.submission_status == "na":
            row.append(u"Not Applicable")
        elif cus.submission_status == 'np' or cus.submission_status == 'ns':
            row.append(u"Not Pursuing")
        elif cus.submission_status == 'p':
            row.append(u"In Progress")
        else:
            row.append(u"Pursuing")

        for df in df_list:

            if (cus.submission_status == "na" or
                cus.submission_status == 'np' or
                cus.submission_status == 'ns' or
                cus.submission_status == 'p'):  # noqa
                row.append("--")
            else:
                field_class = DocumentationFieldSubmission.get_field_class(df)
                try:
                    _df = df.get_for_creditset(ss.creditset)
                    dfs = field_class.objects.get(credit_submission=cus,
                                                  documentation_field=_df)
                except:
                    row.append('**')
                else:
                    if df.type == 'upload':
                        if dfs.value:
                            try:
                                dfs.value.url
                            except Exception:
                                row.append("")
                            else:
                                row.append("https://reports.aashe.org%s" %
                                           dfs.value.url)
                        else:
                            row.append("")
                    else:
                        # long text has to be truncated for excel
                        if dfs.documentation_field.type == 'long_text':
                            if dfs.value:
                                str_val = dfs.value.replace("\r\n", "\n")
                                if len(str_val) > 32000:
                                    str_val = ("%s [TRUNCATED]" %
                                               str_val[:32000])
                            else:
                                str_val = ""
                            row.append(smart_unicode(str_val))

                        else:
                            if dfs.value:
                                try:
                                    row.append(unicode(dfs.value))
                                except StopIteration:
                                    row.append(
                                        ','.join([unicode(v) for v in dfs.value.all()]))
                            else:
                                row.append(u"--")
        if cus.submission_notes:
            row.append(cus.submission_notes)
        else:
            row.append(u"--")

        try:
            csvWriter.writerow(row)
        except:
            print row
            assert False

    else:
        outfile.close()
        print "Closing file: %s" % outfile.name
        return outfile.name


def export_submissionset_csv(submissionsets, outfilename=None):
    """
        Returns a NamedTemporaryFile with data from each submisisonset
        in submissionsets.
    """
    if not outfilename:
        outfile = NamedTemporaryFile(suffix='.csv', delete=False)
    else:
        path = os.path.dirname(outfilename)
        if not os.path.exists(path):
            os.makedirs(path)
        outfile = open(outfilename, 'wb')

    csvWriter = UnicodeWriter(outfile)

    columns = ["Institution",
               "Type",
               "Date Submitted",
               "Version",
               "Rating",
               "Link"]

    csvWriter.writerow(columns)

    for submissionset in submissionsets:

        scorecard_url = ("https://" +
                         REPORTS_HOST +
                         submissionset.get_scorecard_url())

        csvWriter.writerow([submissionset.institution.name,
                            (submissionset.institution.institution_type or
                             "Unknown"),
                            unicode(submissionset.date_submitted),
                            submissionset.creditset.version,
                            submissionset.rating.name,
                            scorecard_url])

    outfile.close()
    print "Closing file: %s" % outfile.name
    return outfile.name
