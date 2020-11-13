from logging import getLogger

from django.conf import settings
from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer


logger = getLogger('stars')


class JSONForHTMLSerializer(Serializer):
    """
        Serializer that returns JSON when asked for HTML.  Removes
        requirement for requests from web browsers to specify a
        format.
    """
    def to_html(self, data, options):
        return self.to_json(data, options)


class StarsApiResource(ModelResource):
    """
        Base class for STARS API resources.
    """
    class Meta:
        if settings.API_TEST_MODE:
            authentication = Authentication()
            logger.warning('no API authentication active')
        else:
            authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        serializer = JSONForHTMLSerializer()

    def __init__(self, *args, **kwargs):
        super(StarsApiResource, self).__init__(*args, **kwargs)
