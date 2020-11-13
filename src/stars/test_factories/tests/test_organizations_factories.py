from django.test import TestCase

from stars.test_factories import organizations_factories


class OrganizationFactoryTest(TestCase):

    def test_organization_account_num_is_unique(self):
        """Is account_num for Organization unique?"""
        first_organization = organizations_factories.OrganizationFactory()
        second_organization = organizations_factories.OrganizationFactory()
        self.assertNotEqual(first_organization.account_num,
                            second_organization.account_num)
