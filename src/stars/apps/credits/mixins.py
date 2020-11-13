import sys

from django.db import models


class VersionedModel(models.Model):
    previous_version = models.OneToOneField('self', null=True, blank=True,
                                            related_name='_next_version')

    class Meta:
        abstract = True

    @property
    def next_version(self):
        """
            Using a property here because _next_version will throw
            a DoesNotExist exception

            Waiting for: https://code.djangoproject.com/ticket/10227
        """
        try:
            return self._next_version
        except self.__class__.DoesNotExist:  # presumably Object.DoesNotExist
            return None

    def get_for_creditset(self, cs):
        """
            Returns the version of this object for the current creditset
        """

        # Check the creditset version
        if self.get_creditset() == cs:
            return self
        else:
            related_obj = None

            # find a previous version
            current_obj = self
            while current_obj.previous_version != None and not related_obj:
                current_obj = current_obj.previous_version
                if current_obj.get_creditset() == cs:
                    return current_obj

            # find a next version
            current_obj = self
            while current_obj.next_version != None and not related_obj:
                current_obj = current_obj.next_version
                if current_obj.get_creditset() == cs:
                    return current_obj

        return None

    def get_all_versions(self):
        """
            Returns all possible versions of this object
        """

        obj_list = []
        obj = self

        # Get the first version
        while obj.previous_version != None:
            obj = obj.previous_version

        # Work back up to latest
        while obj != None:
            obj_list.append(obj)
            obj = obj.next_version

        return obj_list

    def get_latest_version(self):

        obj = self

        while obj.next_version != None:
            obj = obj.next_version

        return obj

    def get_latest_published_version(self):

        obj = self

        while obj.next_version != None and obj.next_version.get_creditset().is_released() == True:
            obj = obj.next_version

        return obj
