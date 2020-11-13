from django.http import Http404
from django.shortcuts import get_object_or_404

from stars.apps.credits.models import (Category,
                                       Credit,
                                       CreditSet,
                                       Subcategory)


class StructureMixin(object):
    """
        Caches values retrieved from the URL arguments in the view class

        Adds the values to the context if their callback is in
        context_callbacks
    """

    def __init__(self, *args, **kwargs):
        self._structure_cache = {}
        self.context_callbacks = []
        self.update_context_callbacks()
        self.kwargs = kwargs
        super(StructureMixin, self).__init__(*args, **kwargs)

    def set_structure_object(self, key, value):
        self._structure_cache[key] = value

    def get_structure_object(self, key):
        if key in self._structure_cache.keys():
            return self._structure_cache[key]
        else:
            return None

    def add_context_callback(self, method):
        self.context_callbacks.append(method)

    def update_context_callbacks(self):
        pass

    def get_obj_or_call(self,
                        cache_key,
                        kwargs_key,
                        klass,
                        property,
                        use_cache=True):
        """
            Looks up a key in the structure, if it's not there
            uses the class and the property to search it

            returns None if not found
            raises 404 if key is in kwargs, but still not found
        """
        obj = None
        if use_cache:
            obj = self.get_structure_object(cache_key)
        if not obj and kwargs_key in self.kwargs.keys():
            _kwargs = {property: self.kwargs[kwargs_key]}
            try:
                obj = get_object_or_404(klass, **_kwargs)
            except ValueError:
                raise Http404
            self.set_structure_object(cache_key, obj)
        return obj

    def get_structure_as_context(self):
        """
            Returns a dictionary that can be merged with the template context
        """
        return self._structure_cache

    def get_context_data(self, **kwargs):
        """
            Before getting context, run all the structure update methods
        """
        if not self.kwargs:
            self.kwargs = kwargs
        else:
            self.kwargs.update(kwargs)

        # run the callbacks
        for callback in self.context_callbacks:
            getattr(self, callback)()

        _context = super(StructureMixin, self).get_context_data(**kwargs)
        _context.update(self.get_structure_as_context())

        return _context


class CreditsetStructureMixin(StructureMixin):
    """
        This mixin provides access and storage of the CreditSet hierarchy
        using the kwargs from urls.py

        It makes an assumption about the kwargs naming schema:
            /creditset_version/category_abbreviation/subcategory_slug/credit_number/field_id/
    """

    def update_context_callbacks(self):
        super(CreditsetStructureMixin, self).update_context_callbacks()
        self.add_context_callback("get_creditset")
        self.add_context_callback("get_category")
        self.add_context_callback("get_subcategory")
        self.add_context_callback("get_credit")
        self.add_context_callback("get_field")

    def get_creditset(self):
        """
            Attempts to get a creditset.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        return self.get_obj_or_call(
            cache_key='creditset',
            kwargs_key='creditset_version',
            klass=CreditSet,
            property='version'
        )

    def get_category(self):
        """
            Attempts to get a category.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_creditset():
            return self.get_obj_or_call(
                cache_key='category',
                kwargs_key='category_abbreviation',
                klass=self.get_creditset().category_set.all(),
                property='abbreviation'
            )

    def get_subcategory(self):
        """
            Attempts to get a category.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_category():
            return self.get_obj_or_call(
                cache_key='subcategory',
                kwargs_key='subcategory_slug',
                klass=self.get_category().subcategory_set.all(),
                property='slug'
            )

    def get_credit(self):
        """
            Attempts to get a credit.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_subcategory():
            return self.get_obj_or_call(
                cache_key='credit',
                kwargs_key='credit_identifier',
                klass=self.get_subcategory().credit_set.all(),
                property='identifier'
            )

    def get_field(self):
        """
            Attempts to get a field.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """

        if self.get_credit():
            return self.get_obj_or_call(
                cache_key='field',
                kwargs_key='field_id',
                klass=self.get_credit().documentationfield_set.all(),
                property='id'
            )

    def get_current_selection(self):
        """
            Determine which component is newest
        """
        key = 'current'
        current = self.get_structure_object(key)
        if not current:
            current = self.get_creditset()
            if self.get_category():
                current = self.get_category()
                if self.get_subcategory():
                    current = self.get_subcategory()
                    if self.get_credit():
                        current = self.get_credit()
        self.set_structure_object(key, current)
        return current

    def get_creditset_nav(self, url_prefix="/"):
        """
            Generates the outline list for the django-collapsing-menu
        """
        current = self.get_current_selection()
        outline = []

        # Top Level: Categories
        for cat in self.get_creditset().category_set.all():
            cat_item = {
                'title': cat.title,
                'bookmark': self.get_category_url(cat, url_prefix),
                'children': [],
                'attrs': {'id': cat.id}
            }
            if current == cat:
                cat_item['attrs']['class'] = 'active'

            # Second Level: Subcategories
            for sub in cat.subcategory_set.all():
                sub_item = {
                    'title': sub.title,
                    'bookmark': self.get_subcategory_url(sub, url_prefix),
                    'children': [],
                    'attrs': {'id': sub.id}
                }
                if current == sub:
                    sub_item['attrs']['class'] = 'active'

                # Third Level: T1 Credits
                for credit in sub.credit_set.all().filter(type='t1'):
                    c_item = {
                        'title': credit.__unicode__(),
                        'url': self.get_credit_url(credit, url_prefix),
                        'attrs': {'id': credit.id}
                    }
                    if current == credit:
                        c_item['attrs']['class'] = "active"

                    sub_item['children'].append(c_item)

                # Fourth Level: T2 Credits
                t2_qs = sub.credit_set.all().filter(type='t2')
                if t2_qs.count() > 0:
                    t2_header_item = {
                        'title': "Tier 2 Credits",
                        'children': []
                    }
                    for t2 in t2_qs:
                        t2_item = {
                            'title': t2.__unicode__(),
                            'url': self.get_credit_url(t2, url_prefix),
                            'attrs': {'id': t2.id}
                        }
                        if current == t2:
                            t2_item['attrs']['class'] = "active"

                        t2_header_item['children'].append(t2_item)

                    sub_item['children'].append(t2_header_item)

                cat_item['children'].append(sub_item)

            outline.append(cat_item)

        return outline

    def get_category_url(self, category, url_prefix="/"):
        """ The default link for a category. """
        return "%s%s/%s/" % (url_prefix,
                             category.creditset.version,
                             category.abbreviation)

    def get_subcategory_url(self, subcategory, url_prefix="/"):
        """ The default link for a category. """
        return "%s%s/" % (self.get_category_url(subcategory.category,
                                                url_prefix),
                          subcategory.slug)

    def get_credit_url(self, credit, url_prefix="/"):
        """ The default credit link. """
        return "%s%s/" % (self.get_subcategory_url(credit.subcategory,
                                                   url_prefix),
                          credit.number)


class CreditNavMixin(object):
    """Class-based mix-in view that can

            - extract the Category, Subcategory, and Credit
              from the variables passed to __call__()

            - provide the outline for the left nav menu for the CreditSet

        Thoughts:

            - use a `get_context_from_request` method so that it can
              be used with mixins
    """

    def get_creditset_selection(self, request, creditset, **kwargs):
        """
            Gets the Category/Subcategory/Credit from the kwargs
            returns a tuple: (category, subcategory, credit)
            assumes the naming scheme: category_id/subcategory_id/credit_id
        """

        category = None
        subcategory = None
        credit = None

        # Get the CategorySubmission
        if 'category_id' in kwargs:
            category = get_object_or_404(Category,
                                         id=kwargs['category_id'],
                                         creditset=creditset)

            # Get the SubcategorySubmission
            if 'subcategory_id' in kwargs:
                subcategory = get_object_or_404(Subcategory,
                                                id=kwargs['subcategory_id'],
                                                category=category)

                # Get the Credit
                if 'credit_id' in kwargs:
                    credit = get_object_or_404(Credit,
                                               id=kwargs['credit_id'],
                                               subcategory=subcategory)

        return (category, subcategory, credit)

    def get_creditset_navigation(self, creditset,
                                 url_prefix=None, current=None):
        """
            Provides a list of categories for a given `creditset`, each with a
            subcategory dict containing a list of subcategories, each
            with credits and tier2 credits dicts containing lists of
            credits

            Category:
                {'title': title, 'url': url, 'subcategories': subcategory_list}
            Subcategory:
                {'title': title, 'url': url, 'credits': credit_list,
                 'tier2': credit_list}
            Credit:
                {'title': title, 'url': url}

        """
        outline = []
        # Top Level: Categories
        for cat in creditset.category_set.all():

            subcategories = []

            # Second Level: Subcategories
            for sub in cat.subcategory_set.all():
                credits = []
                tier2 = []

                # Third Level: Credits
                for credit in sub.credit_set.all():
                    c = {
                            'title': credit.__unicode__(),
                            'url': self.get_credit_url(credit, url_prefix),
                            'id': credit.id,
                            'selected': False,
                        }
                    if current == credit:
                        c['selected'] = True
                    if credit.type == 't1':
                        credits.append(c)
                    elif credit.type == 't2':
                        tier2.append(c)

                temp_sc = {'title': sub.title,
                           'url': self.get_subcategory_url(sub, url_prefix),
                           'credits': credits,
                           'tier2': tier2,
                           'id': sub.id,
                           'selected': False}
                if current == sub:
                    temp_sc['selected'] = True

                subcategories.append(temp_sc)

            temp_c = {'title': cat.title,
                      'url': self.get_category_url(cat, url_prefix),
                      'subcategories': subcategories,
                      'id': cat.id,
                      'selected': False}
            if current == cat:
                temp_c['selected'] = True
            outline.append(temp_c)

        return outline

    def get_category_url(self, category, url_prefix=None):
        """ The default link for a category. """
        raise (NotImplementedError,
               "Your inheriting class needs to define this")

    def get_subcategory_url(self, subcategory, url_prefix=None):
        """ The default link for a category. """
        raise (NotImplementedError,
               "Your inheriting class needs to define this")

    def get_credit_url(self, credit, url_prefix=None):
        """ The default credit link. """
        raise (NotImplementedError,
               "Your inheriting class needs to define this")
