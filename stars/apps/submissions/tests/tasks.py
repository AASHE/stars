"""Tests for apps.submissions.tasks.
"""
from unittest import TestCase

from django.contrib.auth.models import User
import testfixtures

from stars.apps.submissions import tasks
from stars.test_factories import (InstitutionFactory, SubmissionSetFactory,
                                  UserFactory)

def mock_migrate_ss_version(old_ss, new_cs):
    return new_cs

class TasksTest(TestCase):

    def test_perform_migration_logging(self):
        """Does perform_migration log an error when there's no email template?
        """
        submissionset = SubmissionSetFactory()
        user = UserFactory()

        with testfixtures.LogCapture('stars.user') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.submissions.tasks.migrate_ss_version',
                          mock_migrate_ss_version)
                tasks.perform_migration(submissionset, submissionset,
                                        user)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Migration email template missing'))