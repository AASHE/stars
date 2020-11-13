from os.path import basename
import sys

from django.template.defaultfilters import stringfilter
from django import template

from stars.apps.credits.models import Choice
from stars.apps.submissions.models import Boundary


register = template.Library()


def _get_field(doc_field, field_list):
    for f in field_list:
        if f.documentation_field == doc_field:
            return f
    return None


@register.inclusion_tag('institutions/scorecards/field_detail.html',
                        takes_context=True)
def show_submission_field(context):
    context['field'] = _get_field(context['field'],
                                  context['submission_field_list'])
    return context


@register.inclusion_tag('institutions/pdf/field_detail.html',
                        takes_context=True)
def show_submission_field_pdf(context):
    context['field'] = _get_field(context['field'],
                                  context['submission_field_list'])
    return context


@register.inclusion_tag('institutions/scorecards/field_formatting.html',
                        takes_context=True)
def show_submission_field_inside_table(context):
    context['field'] = _get_field(context['field'],
                                  context['submission_field_list'])
    return context


@register.inclusion_tag('institutions/pdf/field_formatting.html',
                        takes_context=True)
def show_submission_field_inside_table_pdf(context):
    context['field'] = _get_field(context['field'],
                                  context['submission_field_list'])
    return context


@register.inclusion_tag('institutions/tags/boundary_display.html')
def show_boundary(submission):
    """
        Display the data from the submission boundary
    """
    # Generate the feature table
    features = [
                    ("Agricultural School", 'ag_school'),
                    ("Medical School", 'med_school'),
                    ("Pharmacy School", 'pharm_school'),
                    ("Public Health", 'pub_health_school'),
                    ("Veterinary School", 'vet_school'),
                    ("Satellite", 'sat_campus'),
                    ("Hospital", 'hospital'),
                    ("Farm", 'farm'),
                    ("Agricultural experiment station", 'agr_exp'),
                ]

    # row obj: {'title', 'present', 'included', 'acres', 'details'}
    feature_table = []
    try:
        for k, p in features:
            d = {
                    'title': k,
                    'present': getattr(submission.boundary,
                                       '%s_present' % p),
                    'included': getattr(submission.boundary,
                                        '%s_included' % p),
                    'details': getattr(submission.boundary,
                                       "%s_details" % p),
                    'id': p
                 }
            if hasattr(submission.boundary, "%s_acres" % p):
                d['acres'] = getattr(submission.boundary, "%s_acres" % p)
            else:
                d['acres'] = None
            feature_table.append(d)
    except Boundary.DoesNotExist:
        pass

    return {'feature_table': feature_table, 'submissionset': submission}


@register.inclusion_tag('institutions/tags/crumbs.html')
def show_scorecard_crumbs(object):
    """
        Displays the crumb navigation for a particular object in the
        Reports Tool
    """
    # @todo: This is a duplicate of the submissions crumbs tag /
    # template = only the link method differs
    object_set = []
    parent = object
    while parent:
        print >> sys.stderr, parent.__class__.__name__
        object_set.insert(0, parent)
        parent = parent.get_parent()

    return {'object_set': object_set}


@register.inclusion_tag('institutions/tags/reporting_field.html')
def show_reporting_field(field, hide_empty_field=False):
    """
        Displays a submission reporing field in the Reports Tool
        Optionally, it will hide fields that do not have any value submitted
    """
    format_method = {
        'text': _get_text_context,
        'long_text': _get_text_context,
        'numeric': _get_text_context,
        'boolean': _get_boolean_context,
        'choice': _get_choice_context,
        'multichoice': _get_choice_context,
        'url': _get_url_context,
        'date': _get_date_context,
        'upload': _get_upload_context,
        'calculated': _get_text_context
    }
    context = format_method.get(field.documentation_field.type,
                                _get_text_context)(field)

    context.update({
        'show_field': ((not hide_empty_field) or
                       (context['field_value'] is not None)),
        'field': field
    })

    return context


def _get_text_context(field):
    text = field.get_value()
    units = field.documentation_field.units
    return {'field_value': text if text else None,
            'units': units if (text and units) else ''}


def _get_date_context(field):
    date = field.get_value()
    return {'field_value': date.strftime("%b. %d, %Y") if date else None}


def _get_boolean_context(field):
    value = field.get_value()
    return {
        'field_value': 'Yes' if value else 'No' if value is not None else None}


def _get_url_context(field):
    url = field.get_value()
    if url:
        return {'url': url,
                'field_value': url}
    else:
        return {'field_value': None}


def _get_upload_context(field):
    filepath = field.get_value()
    if filepath:
        filename = basename(str(filepath))
        url = filepath.url if filepath.url else ''
        return {'url': url,
                'field_value': filename}
    else:
        return {'field_value': None}


def _get_choice_context(field):
    choices = list(Choice.objects.filter(
        documentation_field=field.documentation_field))
    # for consistency, process single choice as a 1 element list
    if field.documentation_field.type == 'choice':
        field_choices = [field.get_value()]
    else:  # multi-choice fields have a list of values
        field_choices = field.get_value()

    # mark all the selected choices
    at_least_one_selected = False
    for choice in choices:
        if choice in field_choices:
            choice.is_selected = True
            at_least_one_selected = True
        else:
            choice.is_selected = False

    units = field.documentation_field.units

    return {
        'choices': [{'choice': c.choice,
                     'is_selected': c.is_selected} for c in choices],
        'units': units if units else '',
        'field_value': (True if at_least_one_selected else None)
    }


def charwrap(value, arg):
    """
    Wraps characters at specified line length with a <br/> tag

    Argument: number of characters to wrap the text at.

    Example {% field.value|charwrap:80 %}
    """
    converted = ""
    temp_val = value
    while len(temp_val) > int(arg) and int(arg) > 0:
        converted += "%s<br/>\n" % temp_val[:int(arg)]
        temp_val = temp_val[int(arg):]
    converted += temp_val
    return converted


charwrap.is_safe = True
charwrap = stringfilter(charwrap)
register.filter(charwrap)


def wraplinks(text, length):
    """
        Takes a string of HTMl and updates it to insert breaks
        before and after links and wrap them to a certain `length`

        For example:

        text = "<p>Check this <a href='URL'>http://boguslink.com</a> out!</p>"
        {{ text|wraplinks:7 }}

        "<p>Check this
           <br/>
           <a href='URL'>
             http://<br/>bogusli<br/>nk.com
           </a>
           <br/>
           out!
         </p>"
    """
    import re
    link_re = "<a href=[\"'](?P<url>.*?)[\"']>(?P<title>.*?)</a>"

    def wrapper(m):
        return ("<a href=\"%s\"><br/>\n%s<br/>\n</a>" %
                (m.group('url'), charwrap(m.group('title'), length)))

    return re.sub(link_re, wrapper, text)

wraplinks.is_safe = True
wraplinks = stringfilter(wraplinks)
register.filter(wraplinks)
