from renewal_tests import RenewalTest

from views import (AccountCreateViewTest, AccountDeleteViewTest,
                   AccountEditViewTest, AccountListViewTest,
                   InstitutionPaymentsViewTest, MigrateDataViewTest,
                   MigrateOptionsViewTest, MigrateVersionViewTest,
                   PendingAccountDeleteViewTest,
                   ResponsiblePartyCreateViewTest,
                   ResponsiblePartyDeleteViewTest,
                   ResponsiblePartyEditViewTest,
                   ResponsiblePartyListViewTest, ShareDataViewTest,
                   SubscriptionCreateViewTest,
                   SubscriptionPaymentCreateBaseViewTest,
                   SubscriptionPaymentCreateViewTest,
                   SubscriptionPaymentOptionsViewTest)

__test__ = {
    'RenewalTest': RenewalTest,
    'AccountCreateViewTest': AccountCreateViewTest,
    'AccountDeleteViewTest': AccountDeleteViewTest,
    'AccountEditViewTest': AccountEditViewTest,
    'AccountListViewTest': AccountListViewTest,
    'InstitutionPaymentsViewTest': InstitutionPaymentsViewTest,
    'MigrateDataViewTest': MigrateDataViewTest,
    'MigrateOptionsViewTest': MigrateOptionsViewTest,
    'MigrateVersionViewTest': MigrateVersionViewTest,
    'PendingAccountDeleteViewTest': PendingAccountDeleteViewTest,
    'ResponsiblePartyCreateViewTest': ResponsiblePartyCreateViewTest,
    'ResponsiblePartyDeleteViewTest': ResponsiblePartyDeleteViewTest,
    'ResponsiblePartyEditViewTest': ResponsiblePartyEditViewTest,
    'ResponsiblePartyListViewTest': ResponsiblePartyListViewTest,
    'ShareDataViewTest': ShareDataViewTest,
    'SubscriptionPaymentOptionsViewTest': SubscriptionPaymentOptionsViewTest,
    'SubscriptionPaymentCreateBaseViewTest':
        SubscriptionPaymentCreateBaseViewTest,
    'SubscriptionCreateViewTest': SubscriptionCreateViewTest,
    'SubscriptionPaymentCreateViewTest': SubscriptionPaymentCreateViewTest,
    }
