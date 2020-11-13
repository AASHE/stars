from django.contrib import messages
from django.forms.forms import BoundField
from django.utils.html import conditional_escape
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.safestring import mark_safe

from stars.apps.helpers.forms.forms import Confirm


def object_editing_list(request, object_list, form_class, ignore_errors=False,
                        ignore_post=False, ignore_objects=[]):
    """
        This is a helper function that reduces duplicate code for
        processing multi-row editing forms.

        It returns a list of (object, editing form) sets the model
        form should have a __cmp__ function for displaying forms in
        correct sort order.

        If you want to ignore the post and just get the list of forms,
        use ignore_post.

        ignore_objects are object that may not have been included in
        the post, such as a new objects.
    """
    errors = False
    saved = False
    object_editing_list = []
    sorted_list = []

    # save any forms that were editted
    if request.method == 'POST' and not ignore_post:
        for obj in object_list:
            form = form_class(request.POST, instance=obj,
                              prefix="editing_%d" % obj.id)
            object_editing_list.append({'obj': obj, 'form': form})
            if obj not in ignore_objects:
                if form.is_valid():
                    if form.has_changed():
                        obj = form.save()
                        saved = True
                else:
                    # DEBUG:
                    # print "Form is not valid: %s %s %s" % (
                    #     form.errors, form['name'].errors,
                    #     form['minimal_score'].errors)
                    errors = True
                    sorted_list.append(obj)
        if saved:
            sorted_list.sort()
    else:
        sorted_list = object_list

    if errors and not ignore_errors:
        messages.error(request,
                       "%s: Please correct the errors below" %
                       _get_form_label(form_class, True))
    elif saved:
        messages.success(request,
                         "%s : Changes were saved successfully." %
                         _get_form_label(form_class, True))

    # create the forms for editing the objects (forms are re-created
    # here to potentially update order)
    if not errors or ignore_errors:
        object_editing_list = []
        for obj in sorted_list:
            form = form_class(instance=obj, prefix="editing_%d" % obj.id)
            object_editing_list.append({'obj': obj, 'form': form})

    return [object_editing_list, saved]


def object_ordering(request, object_list, form_class, ignore_errors=True,
                    ignore_post=False, ignore_objects=[]):
    """
        This is a helper function that reduces duplicate code for
        processing reordering submissions.

        It returns a list of (object, ordering form) sets.

        The model form should have a __cmp__ function for ordering.

        If you are editing more than just the ordering data set
        ignore_errors to False.

        If you want to ignore the post and just get the list use ignore_post.

        ignore_objects are object that may not have been included in
        the post, such as a new objects
    """
    errors = False
    reordered = False
    object_ordering = []
    parents = set()
    parent_reordered = False
    # save any forms that were submitted for re-ordering
    sorted_list = []
    if request.method == 'POST' and not ignore_post:
        for obj in object_list:
            form = form_class(request.POST, instance=obj,
                              prefix="ordering_%d" % obj.id)
            object_ordering.append({'obj': obj, 'form': form})

            if obj not in ignore_objects:
                if form.is_valid():
                    if form.has_changed():
                        old_ordinal = obj.ordinal
                        obj = form.save()
                        if obj.ordinal != old_ordinal:
                            # probably the same parent for all objects
                            # in the list
                            parents.add(obj.get_parent())
                            reordered = True
                else:
                    errors = True
                    # we can safely ignore these errors if
                    # ignore_errors, because there is no user input
            sorted_list.append(obj)
        sorted_list.sort()
    else:
        sorted_list = object_list

    if errors and not ignore_errors:
        messages.error(request,
                       "Unable to update order - "
                       "Please correct the errors below")
    elif reordered:
        messages.success(request,
                         "Order was updated successfully.")
        for parent in parents:  # there are just 0 or 1 parents in the
                                # set (I think!)
            # Notify the parent object that its child objects have
            # been re-ordered.
            try:
                parent_reordered = parent.update_ordering()
            except:  # don't worry if object didn't have the required
                     # method... just continue on
                pass
    # If the parent was re-ordered, then the objects in the sorted
    # list are out-of-date - reload them
    if parent_reordered:
        sorted_list = object_list._clone()

    # create the forms for updating the ordinals
    if not errors or ignore_errors:
        object_ordering = []
        for obj in sorted_list:
            form = form_class(instance=obj, prefix="ordering_%d" % obj.id)
            object_ordering.append({'obj': obj, 'form': form})

    return [object_ordering, reordered]


def _get_class_label(klass, method, plural=False):
    """ Helper: Get a user-friendly label for the given class using the given method name"""
    if plural:
        label = "%ss" % getattr(klass, method)() if hasattr(klass, method) \
            else unicode(klass._meta.verbose_name_plural) if hasattr(klass._meta, 'verbose_name_plural') \
            else ''
    else:
        label = getattr(klass, method)() if hasattr(klass, method) \
            else unicode(klass._meta.verbose_name) if hasattr(klass._meta, 'verbose_name') \
            else ''

    return label.capitalize()


def _get_form_label(klass, plural=False):
    """ Helper: Get a user-friendly label for the given form class """
    label = _get_class_label(klass, "form_name", plural)
    return '%s: ' % label if label else ''


def _get_model_label(klass, plural=False):
    """ Helper: Get a user-friendly label for the given model class """
    return _get_class_label(klass, "model_name", plural)


def _perform_save_form(request, instance, prefix, form_class,
                       save_msg="Changes saved successfully", commit=True,
                       show_message=True, fail_msg=None):
    """
        Helper: for internal use only

        If message is True, the save msg or an error message will be
        sent to the user.

        Returns the object form and a saved flag, which is true if the
        form data was saved to the instance.
    """
    if not fail_msg:
        fail_msg = "Please correct the errors below."

    saved = False
    if request.method == 'POST':
        object_form = form_class(request.POST, request.FILES,
                                 instance=instance, prefix=prefix)
        if object_form.is_valid():
            instance = object_form.save(commit=commit)
            if commit:
                saved = True
        # @todo: only send message if form.has_change()
        if saved and show_message:
            messages.success(request,
                             "%s '%s': %s" % (
                                 _get_model_label(instance.__class__),
                                 instance, save_msg))
        elif show_message:
            messages.error(request,
                           "%s%s" % (_get_form_label(form_class), fail_msg))
    else:
        object_form = form_class(instance=instance, prefix=prefix)
    return [object_form, instance, saved]

#    @todo: get a nice name from the form_class


def basic_save_form(request, instance, prefix, form_class, commit=True,
                    show_message=True, fail_msg=None):
    """
        Provides basic form handling for saving an existing model.

        Returns the object form and a saved flag, which is true if the
        form data was saved to the instance.
    """
    (object_form, instance, saved) = _perform_save_form(
        request, instance, prefix, form_class, commit=commit,
        show_message=show_message, fail_msg=fail_msg)
    return [object_form, saved]


def basic_save_new_form(request, instance, prefix, form_class, commit=True, fail_msg=None):
    """
        Provides basic form handling for saving a new model
        Returns the object form and a saved flag, which is true if the form data was saved to the instance
    """
    (object_form, instance, saved) = _perform_save_form(request, instance, prefix,
                                                        form_class, save_msg="Created successfully", commit=commit, fail_msg=fail_msg)
    if saved:
        try:  # Notify the parent object that a new child object was just added.
            instance.get_parent().update_ordering()
        except:  # if parent didn't have an update_ordering method, no worries!
            pass
    return [object_form, saved]


def save_new_form_rows(request, prefix, form_class, instance_class,
                       **instance_constructor_args):
    """
        Provides form handling for saving a list of new models.

        Intended to work with the clone_form_row.js script, which
        relies on a the HiddenCounterForm to count new forms.

        Assumes that all instances have the same parent, usually
        specified by the instance_constructor_args

          prefix for instance forms in request
          form_class - the form class for saving an instance
          instance_class - duh
          instance_constructor_args - passed as:
              instance_class(instance_constructor_args)

        Returns a list of new instances, and an error flag, which is
        true if any errors were encountered saving the forms.
    """
    from stars.apps.helpers.forms.forms import HiddenCounterForm
    errors = []
    instances = []
    if request.method == 'POST':
        count_form = HiddenCounterForm(request.POST)
        if count_form.is_valid():
            count = int(count_form.cleaned_data['counter'])
            for i in xrange(count):
                new_instance = instance_class(**instance_constructor_args)
                (object_form, new_instance, saved) = _perform_save_form(
                    request, new_instance, '%s_new%s' % (prefix, str(i)),
                    form_class, show_message=False)
                if saved:
                    instances.append(new_instance)
                else:
                    errors.append(object_form.errors)
            if errors:  # this error message will not be pretty!
                messages.error(request,
                               "%s: %s" % (_get_form_label(form_class), errors))
            elif count > 0:
                messages.success(request,
                                 "%s new %s were created successfully." %
                                 (count, _get_model_label(instance_class,
                                                          plural=True)))
        else:
            messages.error(request,
                           "%s: %s" % (_get_form_label(form_class),
                                       count_form.errors['counter']))

    if len(instances) > 0:
        try:  # Notify the parent object that new children objects were
              # just added - assumes they all have the same parent.
            instances[0].get_parent().update_ordering()
        except:  # if parent didn't have an update_ordering method, no worries!
            pass
    return [instances, len(errors) > 0]


def confirm_form(request, instance=None):
    """
        Provides basic form handling for confirming an action or change.
        Returns (form, confirmed), where
         - form is the confirmation form and
         - confirmed is True if the form was POST'ed and the user submitted a confirmation,
                        False if the form was POST'ed and the user did not confirm (not really possible),
                        None if the form was not POST'ed
    """
    confirmed = None
    if request.method == "POST":
        form = Confirm(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm']:
                confirmed = True
            else:
                confirmed = False
    else:
        form = Confirm()
    if instance:
        form.instance = instance
    return (form, confirmed)


def confirm_unlock_form(request, instance):
    """
        Provides basic form handling for confirming unlock for a
        Credit Set (perhaps this will be generalized in future.

        Uses instance.unlock() to perform the unlock.

        Returns (form, unlocked), where form is the confirmation form
        and unlocked is True if the form was POST'ed and the unlock
        performed successfully.
    """
    (form, unlocked) = confirm_form(request, instance)
    if unlocked:
        msg_parms = (_get_model_label(instance.__class__), unicode(instance))
        instance.unlock()
        messages.success(request, "%s %s was unlocked." % msg_parms)

    return (form, unlocked)


def confirm_delete_form(request, instance, delete_method=None):
    """
        Provides basic form handling for confirming and deleting an
        existing model.

        Uses instance.delete() to perform the deletion if no
        delete_method is supplied.

        Returns (form, deleted), where form is the delete confirmation
        form and deleted is True if the form was POST'ed and the
        deletion performed successfully.
    """
    (form, deleted) = confirm_form(request, instance)
    if deleted:
        msg_parms = (_get_model_label(instance.__class__), unicode(instance))
        if not delete_method:
            delete_method = instance.delete
        delete_method()
        messages.success(request, "%s %s was deleted." % msg_parms)

    return (form, deleted)


def confirm_delete_and_update_form(request, instance):
    """
        Exactly as above, but calls instance.delete_and_update() to perform the deletion.
    """
    return confirm_delete_form(request, instance, instance.delete_and_update)

#  Not used anywhere (AFAICT) and duplicates work of form rendering templates
# def two_column_layout(form):
#    """
#        Helper function that displays a form in two columns
#        mostly copied from django.forms.forms.py
#        _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
#    """
#    # My additions
#    left_column_row = u'<tr><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td>'
#    right_column_row = u'<th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>'
#    end_odd_row = u"</tr>"
#    error_row = u'<li>%s</li>'
#    row_ender = u"</td></tr>"
#    errors_on_separate_row = False
#    help_text_html = u'<br />%s'
#    error_row = u'<tr><td colspan="4">%s</td></tr>'
#
#    top_errors = form.non_field_errors() # Errors that should be displayed above all fields.
#    output, hidden_fields = [], []
#    counter = 0
#    for name, field in form.fields.items():
#        bf = BoundField(form, field, name)
#        bf_errors = form.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
#        if bf.is_hidden:
#            if bf_errors:
#                top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
#            hidden_fields.append(unicode(bf))
#        else:
#            if bf.label:
#                label = conditional_escape(force_unicode(bf.label))
#                # Only add the suffix if the label does not end in
#                # punctuation.
#                if form.label_suffix:
#                    if label[-1] not in ':?.!':
#                        label += form.label_suffix
#                label = bf.label_tag(label) or ''
#            else:
#                label = ''
#            if field.help_text:
#                help_text = help_text_html % force_unicode(field.help_text)
#            else:
#                help_text = u''
#            if counter % 2 == 0:
#                output.append(left_column_row % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
#            else:
#                output.append(right_column_row % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
#            counter += 1
#    if counter % 2:
#        output[-1] += end_odd_row
#    if top_errors:
#        output.insert(0, error_row % force_unicode(top_errors))
#    if hidden_fields: # Insert any hidden fields in the last row.
#        str_hidden = u''.join(hidden_fields)
#        if output:
#            last_row = output[-1]
#            # Chop off the trailing row_ender (e.g. '</td></tr>') and
#            # insert the hidden fields.
#            #if not last_row.endswith(row_ender):
#                # This can happen in the as_p() case (and possibly others
#                # that users write): if there are only top errors, we may
#                # not be able to conscript the last row for our purposes,
#                # so insert a new, empty row.
#                #last_row = left_column_row % {'errors': '', 'label': '', 'field': '', 'help_text': ''}
#                #output.append(last_row)
#            output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
#        else:
#            # If there aren't any rows in the output, just append the
#            # hidden fields.
#            output.append(str_hidden)
#    return mark_safe(u'\n'.join(output))
