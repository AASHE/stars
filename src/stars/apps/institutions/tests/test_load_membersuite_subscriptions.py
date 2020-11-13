"""
    Test subscriptions syncing with membersuite
"""
from datetime import timedelta, datetime
from django.test import TestCase
from stars.apps.institutions.models import Subscription
from stars.apps.institutions.management.commands import (
    load_membersuite_subscriptions)

VERBOSE = True


Command = load_membersuite_subscriptions.Command


class SubscriptionSyncTest(TestCase):
    """
        - run the command and ensure that subscriptions exist
    """
    # this needs to be re-done.

    # NOTE: I had to generate this fixture after running a local ISS sync
    # It's really only a short-term solution, as it will change next refresh
    # fixtures = ['iss_orgs.json']

    def setUp(self):
        """
            Right now we fake the loading of institutions using fixtures,
            but we need to figure out a better way.
        """
        pass

    # def test_changes_captured(self):
    #     """
    #         - catch subscriptions that have been deleted
    #         - catch a change to a subscription
    #     """
    #     syncCommand = Command()
    #     syncCommand.sync_subscriptions(verbose=VERBOSE)
    #
    #     # change a subscription
    #     # rerun sync and confirm that that subscription is udpated
    #     test_sub = Subscription.objects.all()[0]
    #
    #     sub_ms_id = test_sub.ms_id
    #
    #     old_start = test_sub.start_date
    #     self.assertEqual(old_start, test_sub.start_date)
    #
    #     test_sub.start_date = test_sub.start_date + timedelta(days=1)
    #     test_sub.save()
    #     self.assertNotEqual(old_start, test_sub.start_date)
    #
    #     syncCommand.sync_subscriptions(verbose=VERBOSE)
    #     # refetch from db
    #     test_sub = Subscription.objects.get(ms_id=sub_ms_id)
    #     self.assertEqual(old_start, test_sub.start_date)
    #
    #     # add a bogus subscription
    #     # rerun sync and confirm that bugus subscription was removed
    #     test_sub = Subscription(
    #         ms_id='something_bogus',
    #         ms_institution_id=None,
    #         institution=None,
    #         start_date=datetime.now(),
    #         end_date=datetime.now()
    #     )
    #     test_sub.save()
    #     subscription_list = Subscription.objects.filter(id=test_sub.id)
    #     self.assertEqual(len(subscription_list), 1)
    #
    #     syncCommand.sync_subscriptions(verbose=VERBOSE)
    #     subscription_list = Subscription.objects.filter(id=test_sub.id)
    #     self.assertEqual(len(subscription_list), 0)
