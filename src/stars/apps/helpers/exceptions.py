
"""
    Special exception classes for STARS specific error handling.
"""

class StarsException(Exception):
    """ 
        These exceptions (and sub-classes) represent STARS-specific errors 
        and provide extra parameters so an appropriate response and log entry can be made.
    """
    def __init__(self, who, message, user_message=None):
        """ 
            @param who - who generated this exception?  Usually name of module or function
            @param message - the exception text itself
            @param user_message - a message suitable for rendering to user
        """
        Exception.__init__(self, message)
        self.who = who
        self.user_message=user_message
