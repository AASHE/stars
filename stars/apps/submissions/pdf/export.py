import cStringIO as StringIO
import ho.pisa as pisa
from cgi import escape
import sys, os
from datetime import datetime

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.utils.encoding import smart_str, smart_unicode

from stars.apps.institutions.models import * # required for execfile management func
#from stars.apps.submissions.models import SubmissionSet
from stars.apps.cms.models import Category
from stars.apps.helpers import watchdog

def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a temlate and context
        Returns a StringIO.StringIO object
    """
    
    template = get_template(template_src)
    context = Context(context_dict)
    print >> sys.stderr, "Building PDF"
    print >> sys.stderr, "%s: Generating HTML" % datetime.now()
    html = template.render(context)
    print >> sys.stderr, "%s: Finished HTML" % datetime.now()
    result = StringIO.StringIO()
    
    print >> sys.stderr, "%s: Generating PDF" % datetime.now()
    pdf = pisa.pisaDocument(html, result)
    print >> sys.stderr, "%s: Finished PDF" % datetime.now()

    if not pdf.err:
        return result
    else:
        watchdog.log("PDF Tool", "PDF Generation Failed %s" % html, watchdog.ERROR)
        return None

def link_path_callback(path):
    return os.path.join(settings.MEDIA_ROOT, path)

def build_report_pdf(submission_set):
    """
        Build a PDF export of a specific submission
        store it in outfile, if submitted
        if save if True, the file will be saved
    """
    context = {
                'ss': submission_set,
                'preview': False,
                'media_root': settings.MEDIA_ROOT,
                'project_path': settings.PROJECT_PATH,
                'rating': submission_set.get_STARS_rating(),
                'institution': submission_set.institution,
                'host': "stars.aashe.org",
                'about_text': Category.objects.get(slug='about').content,
            }
    if submission_set.status != 'r':
        context['preview'] = True
    
    return render_to_pdf('institutions/pdf/report.html', context)