"""Logging filters for STARS.
"""
import logging
import os

from stars import settings


class ModuleNameFilter(logging.Filter):
    """Adds 'module_name' to a LogRecord.
    """
    def filter(self, record):
        abs_project_path = os.path.abspath(settings.PROJECT_PATH)
        try:
            record.module_name = record.pathname.split(abs_project_path)[1][1:]
        except IndexError:
            record.module_name = record.pathname
        return True


class RequestFilter(logging.Filter):
    """Adds request info to a LogRecord.
    """
    def filter(self, record):
        record.request_path = record.request.get_full_path()
        record.request_host = record.request.get_host()
        record.request_user = record.request.user
        if hasattr(record.request, 'get'):
            record.request_referer = record.request.get('referer')
        else:
            record.request_referer = '?'
        return True


class UserFilter(logging.Filter):
    """Adds username to a LogRecord.
    """
    def filter(self, record):
        if record.user:
            record.username = record.user.username
        return True
