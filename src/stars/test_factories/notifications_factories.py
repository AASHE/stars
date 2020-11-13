import factory

from stars.apps.notifications.models import EmailTemplate, CopyEmail


class EmailTemplateFactory(factory.DjangoModelFactory):
    FACTORY_FOR = EmailTemplate

    slug = factory.Sequence(lambda i: 'slug-{0}'.format(i))


class CopyEmailFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CopyEmail

    template = factory.SubFactory(EmailTemplateFactory)
