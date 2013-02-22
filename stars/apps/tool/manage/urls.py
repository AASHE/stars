from django.conf.urls.defaults import patterns, url

from views import (AccountCreateView, AccountDeleteView,
                   AccountEditView, AccountListView, ContactView,
                   InstitutionPaymentsView, MigrateDataView,
                   MigrateOptionsView, MigrateVersionView,
                   PendingAccountDeleteView, ResponsiblePartyCreateView,
                   ResponsiblePartyDeleteView, ResponsiblePartyEditView,
                   ResponsiblePartyListView, ShareDataView,
                   SubscriptionCreateView, SubscriptionPaymentCreateView,
                   SubscriptionPaymentOptionsView, ShareThirdPartiesView)

urlpatterns = patterns(
    'stars.apps.tool.manage.views',

    url(r'^contact/$', ContactView.as_view(), name='institution-contact'),

    url(r'^payments/$', InstitutionPaymentsView.as_view(),
        name='institution-payments'),

    # Responsible Party views:
    url(r'^responsible-party/$',
        ResponsiblePartyListView.as_view(),
        name='responsible-party-list'),

    url(r'^responsible-party/create/$',
        ResponsiblePartyCreateView.as_view(),
        name='responsible-party-create'),

    url(r'^responsible-party/(?P<pk>\d+)/edit/$',
        ResponsiblePartyEditView.as_view(),
        name='responsible-party-edit'),

    url(r'^responsible-party/(?P<pk>\d+)/delete/$',
        ResponsiblePartyDeleteView.as_view(),
        name='responsible-party-delete'),

    # User/Account views:
    url(r'^user/$', AccountListView.as_view(),
        name='account-list'),

    url(r'^user/create/$', AccountCreateView.as_view(),
        name='account-create'),

    url(r'^user/(?P<pk>\d+)/edit/$', AccountEditView.as_view(),
        name='account-edit'),

    url(r'^user/(?P<pk>\d+)/delete/$', AccountDeleteView.as_view(),
        name='account-delete'),

    url(r'^pending-user/(?P<pk>\d+)/delete/$',
        PendingAccountDeleteView.as_view(),
        name='pending-account-delete'),

    # Share Data views:
    url(r'^share-data/$', ShareDataView.as_view(),
        name='share-data'),

    url(r'^share-data/third-parties/$', ShareThirdPartiesView.as_view(),
        name='share-third-parties'),

    # Migration views:
    url(r'^migrate/$', MigrateOptionsView.as_view(),
        name='migrate-options'),

    url(r'^migrate/data/(?P<pk>\d+)/$', MigrateDataView.as_view(),
        name='migrate-data'),

    url(r'^migrate/version/(?P<pk>\d+)/$', MigrateVersionView.as_view(),
        name='migrate-version'),

    # Subscription views:
    url(r'^purchase-subscription/',
        SubscriptionPaymentOptionsView.as_view(),
        name='subscription-payment-options'),

    url(r'^subscription/create/$', SubscriptionCreateView.as_view(),
        name='subscription-create'),

    url(r'^subscription/(?P<pk>\d+)/payment/create/$',
        SubscriptionPaymentCreateView.as_view(),
        name='subscription-payment-create'),
)
