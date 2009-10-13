"""
    Django Choice with Other widgets
    Original ChoiceWithOther downloaded from: http://www.djangosnippets.org/snippets/863/
    ... with a few modifications...
    Plus several variations on the theme:
      - Select with Other
      - Multi-Select with Other
"""
import copy

from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class ChoiceWithOtherRenderer(forms.RadioSelect.renderer):
    """RadioFieldRenderer that renders its last choice with a placeholder."""
    def __init__(self, *args, **kwargs):
        super(ChoiceWithOtherRenderer, self).__init__(*args, **kwargs)
        self.choices, self.other = self.choices[:-1], self.choices[-1]

    def __iter__(self):
        for input in super(ChoiceWithOtherRenderer, self).__iter__():
            yield input
        id = '%s_%s' % (self.attrs['id'], self.other[0]) if 'id' in self.attrs else ''
        label_for = ' for="%s"' % id if id else ''
        checked = '' if not force_unicode(self.other[0]) == self.value else 'checked="true" '
        yield '<label%s><input type="radio" id="%s" value="%s" name="%s" %s/> %s</label> %%s' % (
            label_for, id, self.other[0], self.name, checked, self.other[1])

class ChoiceWithOtherWidget(forms.MultiWidget):
    """MultiWidget for use with ChoiceWithOtherField."""
    def __init__(self, choices, units=None):
        widgets = [
            forms.RadioSelect(choices=choices, renderer=ChoiceWithOtherRenderer),
            forms.TextInput
        ]
        super(ChoiceWithOtherWidget, self).__init__(widgets)
        self.units = units

    def decompress(self, value):
        if not value:
            return [None, None]
        return value

    def set_units(self, units):
        self.units = units
        
    def format_output(self, rendered_widgets):
        """Format the output by substituting the "other" choice into the first widget."""
        if (self.units):
            rendered_widgets[1] = "%s <label>%s</label>"%(rendered_widgets[1], self.units)
            
        return rendered_widgets[0] % rendered_widgets[1]


class AbstractChoiceMultiWidget(forms.MultiWidget):
    """ Common methods for custom choice-type multi-widgets """       
    def set_decompress_method(self, decompress):
        """ This MUST be called before using the widget to set the method used to decompress field values. """
        self.decompress = decompress
        
    def _set_choices(self, choices):
        """ When choices are set for this widget, we want to pass those along to the Select widget"""
        self.widgets[0].choices = choices
    def _get_choices(self):
        """ The choices for this widget are the Select widget's choices"""
        return self.widgets[0].choices
    choices = property(_get_choices, _set_choices)
        
    def set_units(self, units):
        self.units = units

    def __deepcopy__(self, memo):
        """ BUG in django MultiWidget - this method really belongs there to make a deep copy of the widgets list """
        obj = copy.deepcopy(super(AbstractChoiceMultiWidget, self), memo)
        memo[id(self)] = obj
        obj.widgets = copy.deepcopy(self.widgets, memo)
        return obj

"""
    Django Select Field with Other
    Based on above, but modified to use a Select rather than Radio
"""
class ChoiceWithOtherSelectWidget(AbstractChoiceMultiWidget):
    """MultiWidget for use with ChoiceWithOtherField."""
    def __init__(self, choices=(), units=None):
        widgets = [
            forms.Select(choices=choices),
            forms.TextInput
        ]
        super(ChoiceWithOtherSelectWidget, self).__init__(widgets)
        self.units = units
        
    def format_output(self, rendered_widgets):
        """Format the output by rendering the "other" choice just below the select widget."""
        if (self.units):
            rendered_widgets[0] = "%s <label>%s</label>"%(rendered_widgets[0], self.units)
            rendered_widgets[1] = "%s <label>%s</label>"%(rendered_widgets[1], self.units)
            
        return "%s<br>%s"%(rendered_widgets[0], rendered_widgets[1])


"""
    Django CheckboxSelectMultiple Field with Other
    Based on above, but modified to use a CheckboxSelectMultiple rather than Radio
"""
class CheckboxSelectMultipleWithOtherWidget(AbstractChoiceMultiWidget):
    """MultiWidget for use with MultipleChoiceWithOtherField."""
    def __init__(self, choices=()):
        widgets = [
            forms.CheckboxSelectMultiple(choices=choices),
            forms.TextInput
        ]
        super(CheckboxSelectMultipleWithOtherWidget, self).__init__(widgets)

    def render(self, name, value, attrs=None):
        """ Gotta override render to ensure value gets decompressed correctly 
            - MultiWidget won't decompress a value that is a list, which, of course, our value is!
        """
        # the 'decompressed' value looks lie this:  [ [list, of, choices], u'other' ]
        # the 'compressed' value is simply a list: [list. of, choices, with, other]
        # the value needs to be decompressed if the first element is not a list!
        if isinstance(value, list) and len(value)>0 and not isinstance(value[0], list):
            value = self.decompress(value)
        return super(CheckboxSelectMultipleWithOtherWidget, self).render(name, value, attrs)
       
    def format_output(self, rendered_widgets):
        """Format the output by rendering the "other" choice into the last choice."""
        # Unfortunately, CheckboxSelectMultiple doesn't usea a renderer like RadioSelect, so we have to hack a little here...
           # This hack assumes CheckboxSelectMultiple widget is rendered as a list;
           # We are trying to insert the 'other' field just before the last </li> tag, containing the 'other' choice.
           # If there are units with that last choice, then insert just before the units.
        #print "formatting: %s"%rendered_widgets[0]
        pre, tag, post = rendered_widgets[0].rpartition('</li>')
        pre, span, units = pre.rpartition("<span class='units'>")
        if span:
            tag = "%s%s%s"%(span, units, tag)
        else:
            pre = units # had to use an rpartition above to get last choice, but that puts content in units if no units are specified - comfusing, eh?
        multi_widget = "%s </label> %s <label>%s%s"%(pre, rendered_widgets[1], tag, post)
        return multi_widget 
