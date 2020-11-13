import datetime
import time

from django.template.defaultfilters import slugify
import factory

from stars.apps.credits.models import (ApplicabilityReason,
                                       Category,
                                       Credit,
                                       CreditSet,
                                       DocumentationField,
                                       Rating,
                                       Subcategory,
                                       Unit)


class CreditSetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CreditSet

    version = factory.Sequence(lambda i: i)
    release_date = datetime.date(1970, 1, 1)
    tier_2_points = 1
    scoring_method = "get_STARS_v2_0_score"
    credit_identifier = "get_1_1_identifier"


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    creditset = factory.SubFactory(CreditSetFactory)
    title = factory.Sequence(
        lambda i: 'Category-{0}.{1}'.format(i, time.time()))
    abbreviation = factory.Sequence(
        lambda i: 'C' + str(i))


class SubcategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Subcategory

    category = factory.SubFactory(CategoryFactory)
    title = factory.Sequence(
        lambda i: 'Subcategory-{0}.{1}'.format(i, time.time()))
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))


class CreditFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Credit

    subcategory = factory.SubFactory(SubcategoryFactory)
    point_value = 1
    identifier = factory.Sequence(
        lambda i: 'Credit-{0}'.format(i))
    title = factory.Sequence(
        lambda i: 'Credit-{0}.{1}'.format(i, time.time()))


class UnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Unit


class TextDocumentationFieldFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DocumentationField

    credit = factory.SubFactory(CreditFactory)
    units = factory.SubFactory(UnitFactory)
    type = 'text'


DocumentationFieldFactory = TextDocumentationFieldFactory


class ApplicabilityReasonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ApplicabilityReason

    credit = factory.SubFactory(CreditFactory)
    ordinal = factory.Sequence(lambda i: i)


class RatingFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Rating

    name = factory.Sequence(
        lambda i: 'Rating-{0}'.format(i))
    creditset = factory.SubFactory(CreditSetFactory)
    minimal_score = 1
