"""
Tests for helpers API.
"""
from stars.apps.api.test import ReadOnlyResourceTestCase
from stars.apps.helpers.models import BlockContent


class BlockContentResourceTestCase(ReadOnlyResourceTestCase):

    multi_db = True
    list_path = "/api/0.1/block_content/"
    detail_path = list_path + "1/"
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    def setUp(self):
        super(BlockContentResourceTestCase, self).setUp()
        BlockContent.objects.create(key="first-block",
                                    content="lorem epsum asdfasedf")
        BlockContent.objects.create(key="second-block",
                                    content="mary had a little lambda")

    def test_get_block_content_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_block_content_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_block_content_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_block_content_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)
