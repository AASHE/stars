from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from django.forms.utils import ErrorList


class WarningList(ErrorList):
    """
    A collection of warnings that knows how to display itself in various formats.
    """

    def as_ul(self):
        if not self:
            return u''
        return mark_safe(u'<ul class="warninglist">%s</ul>'
                         % ''.join([u'<li>%s</li>' % conditional_escape(force_unicode(e)) for e in self]))
