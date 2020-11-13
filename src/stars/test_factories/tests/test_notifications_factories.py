from django.test import TestCase

from stars.apps import notifications
from stars.test_factories import notifications_factories


class EmailTemplateFactoryTest(TestCase):

    def test_slug_is_unique(self):
        """Is the slug for each EmailTemplate unique?"""
        first_email_template = notifications_factories.EmailTemplateFactory()
        second_email_template = notifications_factories.EmailTemplateFactory()
        self.assertNotEqual(first_email_template.slug,
                            second_email_template.slug)


class CopyEmailFactoryTest(TestCase):

    def test_email_template_is_produced(self):
        """Is an EmailTemplate for this CopyEmail produced?"""
        copy_email = notifications_factories.CopyEmailFactory()
        self.assertIsInstance(copy_email.template,
                              notifications.models.EmailTemplate)
