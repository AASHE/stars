import copy
import collections

from django import template
from django import forms

"""
    Thanks:
    http://www.djangosnippets.org/snippets/1019/
"""

register = template.Library()


def get_fieldset(parser, token):
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'bad arguments for %r' % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form)


get_fieldset = register.tag(get_fieldset)


class FieldSetNode(template.Node):
    def __init__(self, fields, variable_name, form_variable):
        self.fields = fields
        self.variable_name = variable_name
        self.form_variable = form_variable

    def render(self, context):

        form = template.Variable(self.form_variable).resolve(context)
        new_form = copy.copy(form)
        new_form.fields = collections.OrderedDict(
            [(key, value) for key, value in form.fields.items() if key in self.fields])

        context[self.variable_name] = new_form

        return u''


# @register.tag(name='fieldset')
def do_collapsing_fieldset(parser, token):
    """
      A collapsing fieldset tag.
      Typical usage::
         {% fieldset legend with field,list as fields from form %}
            {% for field in fields %}
                {{ field }}
            {% endfor %}
        {% endfieldset %}

      Customized usage (use get_fieldset to manually load fields into context, or whatever):
         {% fieldset legend %}
            {% get_fieldset field,list as fields from form
            {% for field in fields %}
                {{ field }}
            {% endfor %}
        {% endfieldset %}

      Additional Optional parameter (works with either syntax):
         initial_state - this gives the css class representing the intial state (e.g, 'expanded', 'collapsed')
                       - default initial_state is 'expanded'
                       - may be any css class (e.g., 'hidden')
                       - special class 'non_collapsing' will render the fieldset 'expanded' and without any collapsing logic.
      Requires:
        - Javascript:  expand_collapse_parent()  is included on page
        - Images: /media/static/images/collapse.png and /media/static/images/expand.png
        - CSS: definitions for at least:  fieldset.collapsed and fieldset.expanded
    """
    try:
        bits = list(token.split_contents())
        if len(bits) > 3:
            legend, with_, fields, as_, variable_name, from_, form = bits[1:8]
            if with_ != 'with' or as_ != 'as' or from_ != 'from':
                raise ValueError
        else:
            legend, fields, variable_name, form = bits[1], '', '', None

        fieldset_css_class = bits[8] if len(
            bits) > 8 else bits[2] if len(bits) == 3 else "'expanded'"

    except ValueError:
        raise template.TemplateSyntaxError(
            "%r expected format is 'legend with field,list as fields from form'" % bits[0])

    legend = parser.compile_filter(legend)
    fieldset_css_class = parser.compile_filter(fieldset_css_class)
    nodelist = parser.parse(('endfieldset',))
    parser.delete_first_token()

    return CollapsingFieldSetNode(legend, fields.split(','), variable_name, form, fieldset_css_class, nodelist)


fieldset = register.tag('fieldset', do_collapsing_fieldset)


class CollapsingFieldSetNode(template.Node):
    def __init__(self, legend, fields, variable_name, form, fieldset_css_class, nodelist):
        self.legend = legend
        self.fields = fields
        self.variable_name = variable_name
        self.form = template.Variable(form) if form else None
        self.fieldset_css_class = fieldset_css_class
        self.nodelist = nodelist

    def render(self, context):

        legend = self.legend.resolve(context)
        fieldset_id = legend.lower().replace(' ', '_')

        if (self.form):
            form = self.form.resolve(context)
            new_form = copy.copy(form)
            new_form.fields = collections.OrderedDict(
                [(key, value) for key, value in form.fields.items() if key in self.fields])
        else:
            form = new_form = None

        fieldset_css_class = self.fieldset_css_class.resolve(context)
        is_collapsing = fieldset_css_class != 'non_collapsing'

        fieldset_attributes = "id='%s' class='%s%s'" % (
            fieldset_id, fieldset_css_class, '' if is_collapsing else ' expanded')
        legend_title = 'Expand / Collapse'
        legend_attributes = "style='cursor: pointer' onclick='expand_collapse_parent(this)'" if is_collapsing else ""
        image, alt = ('/media/static/images/collapse.png',
                      '-') if fieldset_css_class == 'expanded' else ('/media/static/images/expand.png', '+')
        legend_content = "<img src=%s title='Expand/Collapse' alt='%s' /> %s" % (
            image, alt, legend) if is_collapsing else legend

        # There should be a way to render this from a small template file... hmmm.
        start_tags = """
        <fieldset %s>
           <legend class='title' title='%s' %s >
                %s
            </legend>
            <div>
        """ % (fieldset_attributes, legend_title, legend_attributes, legend_content)
        end_tags = """
            </div>
        </fieldset>
        """
        context.push()
        if new_form:
            context[self.variable_name] = new_form
        context['legend'] = legend
        output = "%s%s%s" % (
            start_tags, self.nodelist.render(context), end_tags)
        context.pop()
        return output
