"""
    # basic doctest test suite for auth.

    >>> from stars.apps.auth.aashe import AASHEAuthBackend
    >>> from stars.apps.auth import xml_rpc as auth_rpc
    >>> auth = AASHEAuthBackend()
    >>> # Invalid access attempts.
    >>> print auth.authenticate("it@aashe.org", "wrongpw")
    None
    >>> print auth.authenticate("not-a-user@dummy.com", "pw")
    None
    >>> print auth_rpc.get_user_by_email('not-a-use@dummy.com')
    []
    >>> # Valid access attempts.
    >>> auth.authenticate("stars@aashe.org", "m5&L0.3ld*Rf")
    <User: stars__aashe_org>
    >>> user = auth_rpc.get_user_by_email('ben@aashe.org')[0]
    >>> user['uid']
    '5214'
    >>> user['mail']
    'ben@aashe.org'
    >>> auth.authenticate("STARS@AASHE.ORG", "m5&L0.3ld*Rf")
    <User: stars__aashe_org>
"""
