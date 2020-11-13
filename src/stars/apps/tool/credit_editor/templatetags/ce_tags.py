from django import template

from stars.apps.submissions.models import DocumentationFieldSubmission
from stars.apps.tool.my_submission.forms import SubmissionFieldForm

register = template.Library()


def _get_form(doc_field, editing=False):
    """
        Gets a form for a documentation field
    """
    SubmissionFieldModelClass = DocumentationFieldSubmission.get_field_class(
        doc_field)
    submission_field = SubmissionFieldModelClass(
        documentation_field=doc_field) if SubmissionFieldModelClass else None

    SubmissionFieldFormClass = SubmissionFieldForm.get_form_class(
        submission_field)
    form = SubmissionFieldFormClass(None, instance=submission_field)
    form.fields['value'].widget.attrs = {'class': 'noMCE',
                                         'disabled': 'disabled'}
    return form


@register.inclusion_tag('tool/submissions/tags/documentation_field_form.html')
def show_field_form(doc_field, editing=True):
    """ Displays the submission form for a documentation field """
    return{"documentation_field": doc_field,
           "field_form": _get_form(doc_field, editing),
           "editing": editing}


@register.inclusion_tag('tool/submissions/tags/documentation_field_inside_table.html')
def show_field_form_inside_table(doc_field, editing=True):
    """ Displays the submission form for a documentation field """
    if doc_field != '':
        return{"documentation_field": doc_field,
               "field_form": _get_form(doc_field, editing),
               "editing": editing}


@register.inclusion_tag('tool/credit_editor/tags/crumbs.html')
def show_editor_crumbs(object):
    """ Displays the crumb navigation for a particular object in the Credit Editor """
    object_set = []
    parent = object
    while parent:
        object_set.insert(0, parent)
        try:
            parent = parent.get_parent()
        except AttributeError:
            return {}
    return {'object_set': object_set}


@register.inclusion_tag('tool/credit_editor/tags/dependent_objects.html')
def show_dependent_objects(object, depth=-1):
    """
        Displays a list of dependents of the given Credit model object to the given depth (-1 for all)
        This tag is recursive - it displays the dependency hierarchy to the given depth.
        If a depth is given, the depth'th level (when depth==1) is shown as counts only.
    """
    dependents = [(None, [])]
    if hasattr(object, 'get_dependents'):
        dependents = object.get_dependents()
    return {'dependents': dependents, 'depth': depth-1, 'counts_only': depth == 1}
