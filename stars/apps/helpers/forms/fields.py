"""
    Django Choice with Other fields
    Original ChoiceWithOther downloaded from: http://www.djangosnippets.org/snippets/863/
    ... with a few modifications...
    Plus several variations on the theme:
      - Model Select with Other
      - Model Multi-Select with Other
"""
from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from stars.apps.helpers.forms import widgets 

class ChoiceWithOtherField(forms.MultiValueField):
    """
    ChoiceField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choice the user made, and the "other" field typed in if the choice
    made was the last one.

    @todo: Add doc test

    """
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(widget=forms.RadioSelect(renderer=ChoiceWithOtherRenderer), *args, **kwargs),
            forms.CharField(required=False)
        ]
        widget = widgets.ChoiceWithOtherWidget(choices=kwargs['choices'])
        kwargs.pop('choices')
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ChoiceWithOtherField, self).__init__(widget=widget, fields=fields, *args, **kwargs)

    def compress(self, value):
        if self._was_required and not value or value[0] in (None, ''):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return [None, u'']
        return (value[0], value[1] if force_unicode(value[0]) == force_unicode(self.fields[0].choices[-1][0]) else u'')


class AbstractModelChoiceMultiField(object):
    """ Common methods for custom Model Choice-with-other type fields """

    def set_compress_methods(self, compress, decompress):
        """ This MUST be called before using the field to set the methods used to compress and decompress field values. """
        self.compress = compress
        self.widget.set_decompress_method(decompress)
        
    def _get_other_choice(self):
        """ Return the 'other' Choice object in the list of choices """
        queryset = self.queryset
        if len(queryset) > 0:
            return queryset[len(queryset)-1]  # no negative indexing on QuerySets
        else:
            return None 

       
class ModelChoiceWithOtherField(forms.ModelChoiceField, AbstractModelChoiceMultiField):
    """
    ModelChoiceField for selecting Choice's, with an option for a user-submitted "other" Choice.

    Takes after a MultiField in many ways, but gains more from inheriting from ModelChoiceField 
    
    @todo: Add doc test
    """
    def __init__(self, *args, **kwargs):
        widget = widgets.ChoiceWithOtherSelectWidget
            
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ModelChoiceWithOtherField, self).__init__(None, widget=widget, *args, **kwargs)
        
    def set_units(self, units):
        """ The units to display with each Choice """
        self.widget.set_units(units)

    def clean(self, value):
        """ Returns a single Choice object (which may be a 'bonafide" choice selection, or an'other', user-defined Choice) or None """
        # the incoming, 'decompressed' value looks lie this:  [ choiceId, u'other' ]
        # the 'compressed' return value is a single Choice object
        if value and not isinstance(value, list):
            raise forms.ValidationError('Invalid choice')
        if self._was_required and (not value or value[0] in (None, '')):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return None
        # clean the two physical fields...
        choice = super(ModelChoiceWithOtherField, self).clean(value[0]) 
        other_value = forms.fields.CharField(required=False).clean(value[1]) 

        other_choice = self._get_other_choice()
        if other_choice and choice == other_choice and not other_value:
            raise forms.ValidationError('Value required for %s'%other_choice.choice)
        # the opposite case, got other but last choice not selected, is not really a validation error -
        # more like a warning - leave this to a higher level to send warning about potential lost data.
        
        return self.compress(choice, other_value)


class ModelMultipleChoiceWithOtherField(forms.ModelMultipleChoiceField, AbstractModelChoiceMultiField):
    """
    MultipleChoiceField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choices the user made, and the "other" field typed in if the choice
    made was the last one.

     @todo: Add doc test

    """
    def __init__(self, *args, **kwargs):
        widget = widgets.CheckboxSelectMultipleWithOtherWidget
        
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ModelMultipleChoiceWithOtherField, self).__init__(None, widget=widget, *args, **kwargs)
        self.units = None

    def set_units(self, units):
        """ The units to display with each Choice """
        self.units = units

    def label_from_instance(self, choice):
        """ Add units to the choice """
        label = super(ModelMultipleChoiceWithOtherField, self).label_from_instance(choice)
        if self.units:
            # Hack alert:  widget rendering depends on this units span tag!!!
            return mark_safe("%s <span class='units'>%s</span>"%(label, self.units))
        else:
            return label
 
    def clean(self, value):
        """ Returns a list of selected Choice object, which may be an empty list """
        # the incoming 'decompressed' value looks lie this:  [ [list, of, choice id's], u'other' ]
        # the 'compressed' return value is simply a list: [list. of, Choices, with, other]
        if self._was_required and not value or value[0] in (None, []):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return []
        elif not isinstance(value, list):
            raise forms.ValidationError('Invalid choice')
        else:
            choice_list = value[0]

        # clean the two physical fields...
        choices = super(ModelMultipleChoiceWithOtherField, self).clean(choice_list)
        other_value = forms.fields.CharField(required=False).clean(value[1]) 

        other_choice = self._get_other_choice()
        if other_choice and other_choice in choices and not other_value:
            raise forms.ValidationError('Value required for %s'%other_choice.choice)
        # the opposite case, got other but last choice not selected, is not really a validation error -
        # more like a warning - leave this to a higher level to send warning about potential lost data.
        return self.compress(choices, other_value) 


class ModelMultipleChoiceWithOtherOldField(forms.ModelMultipleChoiceField):
    """
    MultipleChoiceField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choices the user made, and the "other" field typed in if the choice
    made was the last one.

     @todo: Add doc test

    """
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('choices'):
            widget = widgets.CheckboxSelectMultipleWithOtherWidget(choices=kwargs['choices'])
            kwargs.pop('choices')
        else:
            widget = widgets.CheckboxSelectMultipleWithOtherWidget()
        
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ModelMultipleChoiceWithOtherField, self).__init__(None, widget=widget, *args, **kwargs)
        self.units = None

    def set_compress_methods(self, compress, decompress):
        """ This MUST be called before using the field to set the methods used to compress and decompress field values. """
        self.compress = compress
        self.widget.set_decompress_method(decompress)
        
    def set_units(self, units):
        """ The units to display with each Choice """
        self.units = units

    def label_from_instance(self, choice):
        """ Add units to the choice """
        label = super(ModelMultipleChoiceWithOtherField, self).label_from_instance(choice)
        if self.units:
            # Hack alert:  widget rendering depends on this units span tag!!!
            return mark_safe("%s <span class='units'>%s</span>"%(label, self.units))
        else:
            return label
 
    def clean(self, value):
        """ Returns a list of selected Choice object, which may be an empty list """
        # the incoming 'decompressed' value looks lie this:  [ [list, of, choice id's], u'other' ]
        # the 'compressed' return value is simply a list: [list. of, Choices, with, other]
        if self._was_required and not value or value[0] in (None, []):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return []
        elif not isinstance(value, list):
            raise forms.ValidationError('Invalid choice')
        else:
            choice_list = value[0]

        # clean the two physical fields...
        choices = super(ModelMultipleChoiceWithOtherField, self).clean(choice_list)
        other_value = forms.fields.CharField(required=False).clean(value[1]) 

        other_choice = _get_other_choice(self)
        if other_choice and other_choice in choices and not other_value:
            raise forms.ValidationError('Value required for %s'%other_choice.choice)
        # the opposite case, got other but last choice not selected, is not really a validation error -
        # more like a warning - leave this to a higher level to send warning about potential lost data.

        return self.compress(choices, other_value) 
def _get_other_choice(choice_field):
    """ Return the 'other' Choice object in the list of choices """
    queryset = choice_field.queryset
    if len(queryset) > 0:
        return queryset[len(queryset)-1]  # no negative indexing on QuerySets
    else:
        return None
        



class ModelMultipleChoiceCheckboxField(forms.ModelMultipleChoiceField):
    """ Replaces the default ModelMultipleChoiceField widget with checkboxes"""

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('choices'):
            widget = forms.CheckboxSelectMultiple(choices=kwargs['choices'])
            kwargs.pop('choices')
        else:
            widget = forms.CheckboxSelectMultiple()
        super(ModelMultipleChoiceCheckboxField, self).__init__(None, widget=widget, *args, **kwargs)
        self.units = None
        
    def set_units(self, units):
        """ The units to display with each Choice """
        self.units = units

    def label_from_instance(self, choice):
        """ Add units to the choice """
        label = super(ModelMultipleChoiceCheckboxField, self).label_from_instance(choice)
        if self.units:
            return mark_safe("%s <span class='units'>%s</span>"%(label, self.units))
        else:
            return label