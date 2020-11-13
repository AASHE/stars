from stars.apps.third_parties.utils import export_credit_csv

from logging import getLogger
import zipfile

from celery.decorators import task
from django.core.files.temp import NamedTemporaryFile

logger = getLogger('stars.user')


@task()
def build_csv_export(ss):
    print "Starting CSV Export"
    file_list = []  # [name, file]
    cs = ss.creditset
    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            for c in sub.credit_set.all():
                print "exporting: %s" % c
#                 return export_credit_csv(c, [ss])
                file_list.append([c.get_identifier(),
                                  export_credit_csv(c, [ss])])

    tempfile = NamedTemporaryFile(suffix='.zip', delete=False)
    archive = zipfile.ZipFile(tempfile, "w")
    for n, f in file_list:
        archive.write(f, "%s.csv" % n)
    archive.close()
    return tempfile.name


@task()
def build_pdf_export(ss):
    print "Starting PDF Export"
    return ss.get_pdf(template='institutions/pdf/third_party_report.html',
                      refresh=True)
