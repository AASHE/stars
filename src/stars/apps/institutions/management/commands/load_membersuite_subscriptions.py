"""
    load_membersuite_subscriptions.py

    prereqs:
        - ISS is synced with the latest MemberSuite organizations.
"""
from __future__ import unicode_literals

import datetime
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from membersuite_api_client.organizations.services import OrganizationService
from membersuite_api_client.security.services import (
    get_user_for_membersuite_entity)
from membersuite_api_client.subscriptions.services import SubscriptionService
from membersuite_api_client.utils import (get_new_client,
                                          submit_msql_object_query)

from stars.apps.institutions.models import (Institution,
                                            MemberSuiteInstitution,
                                            Subscription)
from stars.apps.institutions.utils import update_institution_properties
from stars.apps.registration.utils import (init_starsaccount,
                                           init_submissionset)


MEMBERSUITE_PREPRODUCTION_DATA_LOAD = datetime.datetime(2017, 4, 9, 20, 0)

logger = logging.getLogger()


_subscription_fee_names = {}


def get_subscription_fee_name(subscription_fee_id, client):
    global _subscription_fee_names
    try:
        return _subscription_fee_names[subscription_fee_id]
    except KeyError:
        subscription_fee = submit_msql_object_query(
            "SELECT Object() FROM SUBSCRIPTIONFEE WHERE ID = '{}'".format(
                subscription_fee_id, client=client))[0]
        _subscription_fee_names[subscription_fee_id] = (
            subscription_fee.fields["Name"])
    return _subscription_fee_names[subscription_fee_id]


def get_access_level(membersuite_subscription, client):
    """Return the access level for `membersuite_subscription`.

    Note a big assumption made here: namely, that the first line
    item on the Order for this Subscription is for this
    Subscription.  I.e., this Subscription doesn't appear in any
    order line except the first.

    """
    order = membersuite_subscription.get_order(client=client)

    if order:  # Subscriptions entered through MemberSuite.
        products = order.get_products(client=client)
        for product in products:
            if "full" in product.name.lower():
                return Subscription.FULL_ACCESS
            elif "basic" in product.name.lower():
                return Subscription.BASIC_ACCESS

    # Subscriptions preloaded into MemberSuite.
    elif (membersuite_subscription.fields["CreatedDate"] ==
          MEMBERSUITE_PREPRODUCTION_DATA_LOAD):
        fee_id = membersuite_subscription.fields["Fee"]
        fee_name = get_subscription_fee_name(
            subscription_fee_id=fee_id,
            client=client)
        if "full" in fee_name.lower():
            return Subscription.FULL_ACCESS
        elif "basic" in fee_name.lower():
            return Subscription.BASIC_ACCESS

    logger.error("Can't determine access level for "
                 "subscription '{}'".format(membersuite_subscription))

    return Subscription.BASIC_ACCESS  # Default access level.


class Command(BaseCommand):
    """
        USAGE: manage.py subscription_etl

        Syncs subscriptions from Membersuite
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.client = get_new_client(request_session=True)
        self.organization_service = OrganizationService(
            client=self.client)

    def handle(self, verbose=False, *args, **options):
        self.sync_subscriptions(verbose=verbose)

    def get_subscriptions(self, verbose=True):
        service = SubscriptionService(client=self.client)

        # pull subscriptions from Membersuite
        membersuite_subscription_list = service.get_subscriptions(
            publication_id=settings.STARS_MS_PUBLICATION_ID,
            verbose=verbose)

        return membersuite_subscription_list

    def update_subscription_from_membersuite(self, stars_subscription,
                                             membersuite_subscription):

        stars_subscription.ms_id = membersuite_subscription.membersuite_id
        stars_subscription.start_date = membersuite_subscription.start_date
        stars_subscription.end_date = membersuite_subscription.expiration_date
        stars_subscription.name = membersuite_subscription.name

        stars_subscription.access_level = get_access_level(
            membersuite_subscription=membersuite_subscription,
            client=self.client)

        try:
            ms_institution = (MemberSuiteInstitution.objects.get(
                membersuite_account_num=membersuite_subscription.owner_id))
        except MemberSuiteInstitution.DoesNotExist:
            try:
                institution_name = membersuite_subscription.name.encode(
                    "ascii")
            except UnicodeEncodeError:
                institution_name = "ORG NAME IS BAD UNICODE"
            print("ERROR: No MemberSuiteInstitution for "
                  "membersuite_subscription: "
                  "(sub) {}, (name) {}, (owner id) {}".format(
                      membersuite_subscription.membersuite_id,
                      institution_name,
                      membersuite_subscription.owner_id))
            return

        stars_subscription.ms_institution = ms_institution

        try:
            institution = Institution.objects.get(
                ms_institution=ms_institution)

        except Institution.DoesNotExist:

            membersuite_stars_liaison = (
                self.organization_service.get_stars_liaison_for_organization(  # noqa
                    organization=ms_institution))

            if not membersuite_stars_liaison:
                logger.error(
                    "No STARS Liaison for Institution {}; "
                    "cannot load STARS subscription".format(
                        stars_subscription.ms_institution.org_name))
                return

            if (not membersuite_stars_liaison.first_name or
                not membersuite_stars_liaison.last_name or
                not membersuite_stars_liaison.email_address):  # noqa
                logger.error(
                    "Incomplete STARS Liaison for Institution {}; "
                    "first_name: {}, last_name {}, email {}; "
                    "cannot Load STARS subscription".format(
                        stars_subscription.ms_institution.org_name,
                        membersuite_stars_liaison.first_name,
                        membersuite_stars_liaison.last_name,
                        membersuite_stars_liaison.email_address))
                return

            # Make one.
            institution = Institution(name=ms_institution.org_name,
                                      ms_institution=ms_institution)
            institution.update_from_iss()
            institution.set_slug_from_iss_institution(institution.aashe_id)

            # institution must have a pk before creating related
            # StarsAccount and SubmissionSet records, so save it
            # now:
            institution.save()

            user, _ = get_user_for_membersuite_entity(
                membersuite_entity=membersuite_stars_liaison)

            # Make a STARS Account:
            init_starsaccount(user, institution)

            # Make Submission Set:
            init_submissionset(institution, user)

            institution.contact_first_name = (
                membersuite_stars_liaison.first_name)
            institution.contact_last_name = (
                membersuite_stars_liaison.last_name)
            institution.contact_title = (
                membersuite_stars_liaison.title)
            institution.contact_email = (
                membersuite_stars_liaison.email_address)

            stars_subscription.institution = institution

        else:
            institution.update_from_iss()
            stars_subscription.institution = institution
            stars_subscription.institution.ms_institution = (
                ms_institution)

        stars_subscription.save()

        # update_institution_properties saves institution.
        update_institution_properties(institution)

    def sync_subscriptions(self, verbose=True):

        # store a list of existing subscription id's
        # those that aren't found in the update, will be removed
        stars_subscription_ms_ids = list(
            Subscription.objects.values_list("ms_id", flat=True))

        membersuite_subscription_list = self.get_subscriptions(verbose=verbose)

        # loop through each MS Subscription
        # add/update local subscriptions as necessary
        # remove from stars_subscription_ids so it won't be archived
        for membersuite_subscription in membersuite_subscription_list:

            # is it an existing subscription?
            if (membersuite_subscription.membersuite_id in
                stars_subscription_ms_ids):  # noqa

                try:
                    stars_subscription = Subscription.objects.get(
                        ms_id=membersuite_subscription.membersuite_id)
                except Subscription.MultipleObjectsReturned:
                    logger.error(
                        "Multiple Subscriptions with ms_id = '{}'".format(
                            membersuite_subscription.membersuite_id))
                    for ms_id in [id for id in stars_subscription_ms_ids
                                  if id ==
                                  membersuite_subscription.membersuite_id]:
                        del(stars_subscription_ms_ids[
                            stars_subscription_ms_ids.index(ms_id)])
                    continue
                else:  # remove this from the list of subscriptions
                       # to be archived  # noqa
                    del(stars_subscription_ms_ids[
                        stars_subscription_ms_ids.index(
                            stars_subscription.ms_id)])
            else:
                if not membersuite_subscription.expiration_date:
                    # Used to raise an error when no expiration_date
                    # was available, then folks started leaving
                    # expiration date blank in MemberSuite to signify
                    # that the subscription hasn't been paid for.
                    # So now we just silently trudge on.
                    continue
                # add a new subscription
                stars_subscription = Subscription(
                    ms_id=membersuite_subscription.membersuite_id)

            # update and save the local subscription
            self.update_subscription_from_membersuite(
                stars_subscription,
                membersuite_subscription)

            stars_subscription.save()

            if stars_subscription.institution:
                stars_subscription.institution.update_current_rating()
                stars_subscription.institution.update_current_subscription()
                stars_subscription.institution.save()
            else:
                logger.error("stars Subscription with id " + str(stars_subscription.pk)
                            + " has no associated Institution. Subscription "
                            "membersuite_id = " + str(membersuite_subscription.membersuite_id))

        # if any id's remain in subscription_id_list they can be archived
        # as they don't exist in MemberSuite anymore

        for ms_id in stars_subscription_ms_ids:
            Subscription.objects.filter(ms_id=ms_id).update(archived=True)
