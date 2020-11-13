"""
    PDF Report Generation
"""
import sys, os
import datetime

from django.template.defaultfilters import slugify

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet
from stars.apps.third_parties.models import ThirdParty

limit_inst_ids = None

def get_ss_list():

    tp = ThirdParty.objects.get(slug="sierra")

    deadline = datetime.date(year=2014, month=6, day=25)

    snapshot_list = tp.get_snapshots().exclude(institution__id=447)
    snapshot_list = snapshot_list.filter(date_submitted__lte=deadline)

    if(limit_inst_ids):
        snapshot_list = snapshot_list.filter(institution__id__in=limit_inst_ids)

    # snapshot_list = snapshot_list | tp.get_snapshots().filter(id='1528')

    # latest_snapshot_list = tp.get_snapshots().filter(institution__id=267)

    inst_list = []
    latest_snapshot_list = [] # only use the latest snapshot
    for ss in snapshot_list:
        if ss.institution.id not in inst_list:
            inst_list.append(ss.institution.id)
            i_ss_list = ss.institution.submissionset_set.filter(status='f').order_by('-date_submitted', '-id').filter(date_submitted__lte=deadline)
            print "Available snapshots for %s" % ss.institution
            for __ss in i_ss_list:
                print "%s, %d" % (__ss.date_submitted, __ss.id)
            latest_snapshot_list.append(i_ss_list[0])
            print "Selected snapshot: %s, %d" % (i_ss_list[0].date_submitted, i_ss_list[0].id)

    print "%d Snapshots" % len(latest_snapshot_list)
    return latest_snapshot_list

def pdf_export():

    ss_list = get_ss_list()

    for ss in ss_list:

        print "generating pdf for: %s" % ss

        outfile = "pdfs/%s-%s" % (slugify(ss.date_submitted), ss.get_pdf_filename())
        pdf = ss.get_pdf(refresh=False, template='institutions/pdf/third_party_report.html')
        os.rename(pdf, outfile)
#         f = open(outfile, 'w')
#         f.write(pdf)

if __name__ == "__main__":
    pdf_export()

    #        pdf = pisa.CreatePDF(html, file(outfile, "wb"), path)

    #    f = open('stars_report.html', 'w')
    #    f.write(smart_str(html))
