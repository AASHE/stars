from django import test
from django.contrib.auth.models import User

from stars.apps.helpers.old_path_preserver import OLD_PATHS_TO_PRESERVE
from stars.test_factories.models import (InstitutionFactory,
                                         StarsAccountFactory,
                                         SubmissionSetFactory)


class OldPathPreserverViewTest(test.TestCase):

    def test_unauthenticated_user(self):
        """Do each of the old paths return 200 if user isn't logged in?
        """
        user = User.objects.create_user(username='john', password='doe')
        user.save()
        InstitutionFactory()

        test_client = test.client.Client()

        for old_path in OLD_PATHS_TO_PRESERVE:
            path = '/' + old_path
            response = test_client.get(path, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_user_with_no_stars_account(self):
        """Do each of the old paths return 200 if user has no StarsAccount?
        """
        user = User.objects.create_user(username='john', password='doe')
        user.save()
        InstitutionFactory()

        test_client = test.client.Client()
        self.assertTrue(test_client.login(username=user.username,
                                          password='doe'))

        for old_path in OLD_PATHS_TO_PRESERVE:
            path = '/' + old_path
            response = test_client.get(path, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_user_with_one_stars_account(self):
        """Do each of the old paths return 200 if user has only 1 StarsAccount?
        """
        user = User.objects.create_user(username='john', password='doe')
        user.save()
        institution = InstitutionFactory()
        StarsAccountFactory(user=user,
                            institution=institution,
                            user_level='admin',
                            terms_of_service=True)
        submission_set = SubmissionSetFactory(institution=institution)
        institution.current_submission = submission_set
        institution.save()

        test_client = test.client.Client()
        self.assertTrue(test_client.login(username=user.username,
                                          password='doe'))

        for old_path in OLD_PATHS_TO_PRESERVE:
            path = '/' + old_path
            response = test_client.get(path, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_user_with_many_stars_accounts(self):
        """Do each of the old paths return 200 if user has > 1 StarsAccount?
        """
        user = User.objects.create_user(username='john', password='doe')
        user.save()
        institution1 = InstitutionFactory()
        institution2 = InstitutionFactory()
        StarsAccountFactory(user=user,
                            institution=institution1,
                            user_level='admin',
                            terms_of_service=True)
        submission_set1 = SubmissionSetFactory(institution=institution1)
        institution1.current_submission = submission_set1
        institution1.save()
        StarsAccountFactory(user=user,
                            institution=institution2,
                            user_level='admin',
                            terms_of_service=True)
        submission_set2 = SubmissionSetFactory(institution=institution1)
        institution2.current_submission = submission_set2
        institution2.save()

        test_client = test.client.Client()
        self.assertTrue(test_client.login(username=user.username,
                                          password='doe'))

        for old_path in OLD_PATHS_TO_PRESERVE:
            path = '/' + old_path
            response = test_client.get(path, follow=True)
            self.assertEqual(response.status_code, 200)
