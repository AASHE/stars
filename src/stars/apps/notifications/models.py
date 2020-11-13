"""
    Templating tool to store email templates in the database
    and allow them to be edited and previewed
"""
from jsonfield import JSONField
from utils import build_message

from django.db import models
from django.core.mail import EmailMessage
from django.conf import settings


class EmailTemplate(models.Model):
    slug = models.SlugField(
        max_length=32, unique=True,
        help_text="Unique name. Please do not change.")
    title = models.CharField(
        max_length=128, help_text='The subjuect line of the email.')
    description = models.TextField()
    content = models.TextField()
    example_data = JSONField(
        help_text="Example context for the template. Do not change.",
        blank=True, null=True)
    active = models.BooleanField(
        help_text=("Checked indicates that the code is using this "
                   "email. For Webdev's use only"), default=False)

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.title

    def get_message(self, content=None, context=None):
        """
            Renders the message with the supplied content.
            Uses self.content if no content is specified
            Uses self.example_data if not context is specified
        """
        if not content:
            content = self.content

        if not context:
            context = self.example_data

        return build_message(content, context)

    def send_email(self, mail_to, context, title=None, attachments=None,
                   reply_to=None):
        """
            Sends an email based on this template to the passed list of emails
            and using the passed context dictionary
        """

        if not settings.EMAIL_REPLY_TO:
            raise NameError('Please define the EMAIL_REPLY_TO '
                            'variable in settings')

        if reply_to is not None:
            reply = reply_to
        else:
            reply = settings.EMAIL_REPLY_TO

        cc_list = []
        bcc_list = []
        for cc in self.copyemail_set.all():
            if cc.bcc:
                bcc_list.append(cc.address)
            else:
                cc_list.append(cc.address)

        if not title:
            title = self.title

        m = EmailMessage(
            subject=title,
            body=build_message(self.content, context),
            to=mail_to,
            cc=cc_list,
            bcc=bcc_list,
            headers={'Reply-To': reply},
            attachments=attachments
        )
        m.send()

    def get_absolute_url(self):
        return "/notifications/preview/%s/" % self.slug


class CopyEmail(models.Model):
    template = models.ForeignKey(EmailTemplate)
    address = models.EmailField()
    bcc = models.BooleanField(help_text='Check to copy this user using BCC',
                              default=False)

    def __str__(self):
        if self.bcc:
            return "BCC: %s" % self.address
        else:
            return "CC: %s" % self.address
