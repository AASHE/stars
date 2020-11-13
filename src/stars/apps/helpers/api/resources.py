"""
    STARS helpers API
"""
from tastypie import fields

from stars.apps.helpers import models
from stars.apps.api.resources import StarsApiResource


class BlockContentResource(StarsApiResource):
    """
        Resource for accessing any BlockContent.
    """
    content = fields.CharField(readonly=True)

    class Meta(StarsApiResource.Meta):
        queryset = models.BlockContent.objects.all().order_by("key")
        resource_name = "block_content"
        fields = ["key", "content"]
        allowed_methods = ["get"]

    def dehydrate_content(self, bundle):
        if bundle.obj.content:
            return bundle.obj.content

    def dehydrate_key(self, bundle):
        if bundle.obj.key:
            return bundle.obj.key
