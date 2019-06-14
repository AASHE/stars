import os
from logging import getLogger

import weasyprint
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from stars.apps.old_cms.models import Category


logger = getLogger('stars')


def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a temlate and context
        Returns a weasyprint.pdf.
    """
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    pdf = weasyprint.HTML(string=html, base_url="file:///")

    return pdf


def link_path_callback(path):
    return os.path.join(settings.MEDIA_ROOT, path)


def build_report_pdf(submission_set, template=None):
    """
        Build a PDF export of a specific submission
        store it in outfile, if submitted
        if save if True, the file will be saved
    """
    context = {'ss': submission_set,
               'preview': False,
               'media_root': settings.MEDIA_ROOT,
               'project_path': settings.PROJECT_PATH,
               'rating': submission_set.get_STARS_rating(),
               'institution': submission_set.institution,
               'host': "reports.aashe.org",
               'about_text': Category.objects.get(slug='about').content,
               'pdf': True}

    if submission_set.status != 'r':
        context['preview'] = True

    if not template:
        template = 'institutions/pdf/report.html'

    pdf = render_to_pdf(template, context)

    # return insert_table_of_contents(pdf)  # table of contents sucks

    return pdf


def insert_table_of_contents(pdf):

    pdf_document = pdf.render()

    table_of_contents_string = generate_outline_str(
        pdf_document.make_bookmark_tree())

    table_of_contents_document = weasyprint.HTML(
        string=table_of_contents_string).render()

    table_of_contents_document.pages.reverse()

    for page in table_of_contents_document.pages:
        pdf_document.pages.insert(0, page)

    return pdf_document


def generate_outline_str(bookmarks, indent=0):
    outline_str = ""
    for i, (label, (page, _, _), children) in enumerate(bookmarks, 1):
        outline_str += (
            "<div>%s%d. %s <span style=\"float:right\">(page %d)</span></div>"
            % (' ' * indent, i, label.lstrip('0123456789. '), page))
        outline_str += generate_outline_str(children, indent + 2)
    return outline_str


def build_certificate_pdf(ss):
    """
        Build a PDF certificate for Institution Presidents
    """
    context = {'ss': ss,
               'project_path': settings.PROJECT_PATH}
    return render_to_pdf('institutions/pdf/certificate.html', context)
