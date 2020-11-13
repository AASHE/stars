from django import template

from stars.apps.submissions.models import CreditUserSubmission, \
    DocumentationFieldSubmission, NumericSubmission


register = template.Library()


@register.inclusion_tag('tool/submissions/tags/available_points.html')
def format_available_points(creditsubmission, use_cache=False):
    """
        Displays the Available points in a readable formats
    """
    value = creditsubmission.get_available_points(use_cache=use_cache)
    adjusted_points = creditsubmission.get_adjusted_available_points()
    popup_text = None

    if adjusted_points == 0:
        value = None
        popup_text = "Total adjusted for non-applicable credits"

    elif creditsubmission.credit.point_variation_reason:
        popup_text = creditsubmission.credit.point_variation_reason

    return {'value': value,
            'popup_text': popup_text,
            "id": "%s_point_variation" % creditsubmission.id}


@register.inclusion_tag('tool/submissions/tags/crumbs.html')
def show_submit_crumbs(object):
    """ Displays the crumb navigation for a particular object in the
        Submission Tool
    """
    object_set = []
    parent = object
    while parent:
        object_set.insert(0, parent)
        parent = parent.get_parent()

    return {'object_set': object_set}


@register.inclusion_tag('tool/submissions/tags/progress_icon.html')
def show_progress_icon(category, size_class=''):
    """ Displays a progress bar showing the percent complete """

    z = category.__class__.__name__

    if z == 'int':
        # if the int is a percent
        numerator = ''
        denominator = ''
        content = ''
        caption = title = "%d%%" % category
        percentage = category
    else:
        numerator = category.get_finished_credit_count()
        denominator = category.get_total_credits()
        if numerator > 0:
            percentage = float(numerator) / float(denominator) * 100
        else:
            percentage = 0  # Fix for css issues
        title = "%.0f / %.0f" % (numerator, denominator)

        if z == "CategorySubmission":
            content = "%.0f / %.0f" % (numerator, denominator)
            caption = "Progress"
        elif z == "SubcategorySubmission":
            content = ""
            caption = "%.0f / %.0f Progress" % (numerator, denominator)
    return {
        'percentage': percentage,
        'numerator': numerator,
        'denominator': denominator,
        'content': content,
        'caption': caption,
        'title': title,
    }


class Icon(object):
    __slots__ = ('title', 'file', 'alt', 'size_class')


@register.inclusion_tag('tool/submissions/tags/status_icon.html')
def show_status_icon(credit, white=0):
    """ Displays an icon representing credit status """
    from stars.apps.submissions.models import CREDIT_SUBMISSION_STATUS_ICONS
    title = credit.get_submission_status_display
    icon, alt = CREDIT_SUBMISSION_STATUS_ICONS.get(credit.submission_status,
                                                   (None, None))
    return {'icon': icon, 'white': white, 'title': title}


@register.inclusion_tag('tool/submissions/tags/payment_icon.html')
def show_payment_type_icon(payment, size_class=''):
    """ Displays an icon representing the payment type """
    from stars.apps.submissions.models import PAYMENT_TYPE_ICONS
    icon = Icon()
    icon.size_class = size_class
    icon.alt = payment.method
    icon.file, icon.title = PAYMENT_TYPE_ICONS.get(payment.method,
                                                   (None, None))
    return {'icon': icon}


@register.inclusion_tag(
    'tool/submissions/tags/documentation_field_inside_table.html')
def show_submission_field_control(form_list, id):
    """ Displays the submission form for a documentation field """
    form = form_list[id]
    return{"documentation_field": form.instance.documentation_field,
           "field_form": form}


def _get_form(doc_field, submission_form):
    form = None
    form_list = submission_form.get_submission_fields_and_forms()
    for ff in form_list:
        if ff['field'].documentation_field == doc_field:
            form = ff['form']
    return form


def get_populate_button_context(doc_field, submissionset):
    _context = {}
    dfcopy = doc_field.copy_from_field

    if dfcopy and submissionset:
        _context['dfcopy'] = dfcopy

        df_class = DocumentationFieldSubmission.get_field_class(dfcopy)
        df_cus = CreditUserSubmission.objects.get(
            credit=dfcopy.credit,
            subcategory_submission__category_submission__submissionset=submissionset
        )
        try:
            df_submission = df_class.objects.get(
                documentation_field=dfcopy,
                credit_submission=df_cus
            )
        except NumericSubmission.DoesNotExist:
            # the documentation field hasn't been created yet,
            # because the credit hasn't been opened
            _context['dfcopyval'] = None
            return _context

        _context['dfcopyval'] = df_submission.value
        if (
            submissionset.institution.prefers_metric_system and
            df_submission.documentation_field.units
        ):
            # in most cases, there will be a metric value, but
            # if there are no units associated with this numeric field
            # then there is no need for a metric value
            _context['dfcopyval'] = df_submission.metric_value

    return _context


@register.inclusion_tag('tool/submissions/tags/documentation_field_form.html')
def show_submission_form_for_field(doc_field, submission_form,
                                   submissionset=None):
    """ Displays the submission form for a documentation field """
    form = _get_form(doc_field, submission_form)

    _context = {
        "documentation_field": doc_field,
        "field_form": form,
        "field_template": "tool/submissions/tags/tabular_field.html",
        "submission_form": submission_form,
        "submissionset": submissionset
    }

    _context.update(get_populate_button_context(doc_field, submissionset))

    return _context


@register.inclusion_tag(
    'tool/submissions/tags/documentation_field_inside_table.html')
def show_submission_form_for_field_inside_table(doc_field,
                                                submission_form,
                                                submissionset=None):
    """ Displays the submission form for a documentation field """
    form = _get_form(doc_field, submission_form)
    _context = {
        "documentation_field": doc_field,
        "field_form": form,
        "submissionset": submissionset}

    _context.update(get_populate_button_context(doc_field, submissionset))
    return _context


@register.simple_tag
def subcategory_has_opt_in_credits(subcategory):
    """Does `subcategory` have any opt-in Credits?"""
    return bool(subcategory.credit_set.filter(is_opt_in=True).count())
