from accounts_factories import UserProfileFactory

from submissions_factories import (BoundaryFactory,
                                   CategorySubmissionFactory,
                                   CreditUserSubmissionFactory,
                                   DocumentationFieldSubmissionFactory,
                                   ResponsiblePartyFactory,
                                   SubmissionSetFactory,
                                   SubcategorySubmissionFactory,
                                   TextSubmissionFactory)

from credits_factories import (ApplicabilityReasonFactory,
                               CategoryFactory, CreditFactory,
                               CreditSetFactory,
                               DocumentationFieldFactory,
                               IncrementalFeatureFactory,
                               RatingFactory, SubcategoryFactory)

from institutions_factories import (ClimateZoneFactory,
                                    InstitutionFactory,
                                    PendingAccountFactory,
                                    StarsAccountFactory,
                                    SubscriptionFactory,
                                    SubscriptionPaymentFactory)

from notifications_factories import EmailTemplateFactory, CopyEmailFactory

from registration_factories import ValueDiscountFactory

from misc_factories import UserFactory

from auth_factories import AASHEAccountFactory

__all__ = [ApplicabilityReasonFactory,
           BoundaryFactory,
           CategoryFactory,
           CategorySubmissionFactory,
           ClimateZoneFactory,
           CopyEmailFactory,
           CreditFactory,
           CreditSetFactory,
           CreditUserSubmissionFactory,
           DocumentationFieldFactory,
           DocumentationFieldSubmissionFactory,
           EmailTemplateFactory,
           IncrementalFeatureFactory,
           InstitutionFactory,
           PendingAccountFactory,
           RatingFactory,
           ResponsiblePartyFactory,
           StarsAccountFactory,
           SubcategoryFactory,
           SubcategorySubmissionFactory,
           SubmissionSetFactory,
           SubscriptionFactory,
           SubscriptionPaymentFactory,
           TextSubmissionFactory,
           UserFactory,
           UserProfileFactory,
           ValueDiscountFactory]
