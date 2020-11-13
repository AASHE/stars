class DummyRequest(object):
    """ A dummy request object used for testing """
    def __init__(self, user):
        self.user = user
        self.path = "/dummy_path/"
        self.host = "carson"
        self.environ = {}

    def get_full_path(self):
        return self.path

    def get_host(self):
        return self.host

    def get(self, *args, **kwargs):
        return ''
