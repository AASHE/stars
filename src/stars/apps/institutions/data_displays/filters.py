"""
    Filters are a way of doing the following.

    Pass the filters to the context:

        available_filters = [{
            'filter_title': <title>,
            'filter_key': <key>,
            'filter_choices': [
                                ('choice1', 'choice1_val'),
                                ('choice2', 'choice2_val')
                            ]
            },]

        selected_filters = [{
            'filter_title': <title>,
            'selected_item_title': <selected_item_title>,
            'del_link': <get_parameters> # a URL encoded link to this page w/out this filter
            },]

    Filters are passed to the view via GET requests:

        ?filter_key=selected_item&filter_key=selected_item

    Filter objects are used to filter data in the Data Displays
    They do their own work, to keep the logic out of the views

        - Generate Querysets for selected items
        - Provide a title for the active filter
        - Get a list of choices

    The FilteringMixin provides all the filtering methods to a view
"""
from django.http import QueryDict


class Filter(object):
    """
        Filters need to be a managed more programatically
        added and removed from the general list where available

        Note: the `key` should be unique to the list of filters
        you are using
    """

    def __init__(self, key, title, item_list, base_qs):
        self.key = key
        self.title = title
        self.item_list = item_list
        self.base_qs = base_qs

    def get_active_title(self, item):
        " A name to display for this filter when active. "

        # Translation from form
        if item == "True":
            item = True
        elif item == "False":
            item = False

        if self.key == "rating__name":
            return "%s Rated Institutions" % item

        for k, v in self.item_list:
            if item == v:
                return k

        return item

    def get_select_list(self):
        """
            This is used to build the pull-down lists and
            always returns a list of tuples despite the
            internal structure of item_list
        """
        return self.item_list

    def get_results(self, item):
        " Returns a queryset with the applied filter for item. "

        if item == 'DO_NOT_FILTER':
            return self.base_qs.exclude(institution__name__icontains="AASHE")
        elif item == 'ALL_OTHER_COUNTRIES':
            return self.base_qs.exclude(
                institution__ms_institution__country='United States').exclude(
                    institution__ms_institution__country='Canada').exclude(
                    institution__name__icontains="AASHE")
        else:
            # convert True and False from text
            if item == "True":
                item = True
            elif item == "False":
                item = False

            kwargs = {self.key: item}

            return self.base_qs.filter(**kwargs).exclude(
                institution__name__icontains="AASHE")

        return self.base_qs.exclude(institution__name__icontains="AASHE")


class RangeFilter(Filter):
    """
        Like a filter, but the item_list adds a min and max:

        Example:

        item_list = [
                ('Title', 'key', min, max),
                ('Under 5,000', 'u5000', 0, 5000 ),
                ('5,000-10,000', 5000-10000', 5000, 10000 ),
                ('Over 10,000', 'o10000', 10000, None ), # None exlcudes the upper bound
           ],
    """

    def get_active_title(self, item):
        " A name to display for this filter when active. "

        for i in self.item_list:
            if i[1] == item:
                return i[0]

    def get_select_list(self):
        """

        """
        select_list = []
        for i in self.item_list:
            select_list.append((i[0], i[1]))
        return select_list

    def get_results(self, item):
        " Returns a queryset with the applied filter for item (key). "

        for i in self.item_list:
            if i[1] == item:
                qs = self.base_qs
                if i[2]:
                    min_kwargs = {"%s__gte" % self.key: i[2]}
                    qs = qs.filter(**min_kwargs)
                if i[3]:
                    max_kwargs = {"%s__lt" % self.key: i[3]}
                    qs = qs.filter(**max_kwargs)
                return qs

        return None


class FilteringMixin(object):
    """
        A mixin that will manage filtering

        Filters are defined in the GET request and stored internally
        as a QueryDict

        Optionally `available_filters` can be overridden to set the
        default filters
    """

    def get_available_filters(self):
        """
            Used to populate the child select using JavaScript
        """
        return []

    def get_context_data(self, **kwargs):

        _context = super(FilteringMixin, self).get_context_data(**kwargs)
        _context['available_filters'] = (
            self.get_available_filters_for_context())
        _context['selected_filters'] = self.get_selected_filters_for_context()
        _context['selected_filters_querydict'] = (
            self.get_selected_filter_querydict())
        _context['get_params'] = self.request.GET.urlencode()
        return _context

    def get_available_filters_for_context(self):
        """
            Convert available_filter_objects to available_filter list

                available_filters = [{
                    'filter_title': <title>,
                    'filter_key': <key>,
                    'filter_choices': [
                                        ('choice1', 'choice1_val'),
                                        ('choice2', 'choice2_val')
                                    ]
                    },]

            I set the choice values to be URLs for easy linking
        """
        available_filters = []
        for f in self.get_available_filters():
            f_dict = {
                'filter_title': f.title,
                'filter_key': f.key,
                'filter_choices': []
            }
            # Populate the choices with URLs
            for i in f.item_list:
                url = "?%s" % self.add_filter_to_querydict(self.request.GET,
                                                           f.key,
                                                           i[1]).urlencode()
                f_dict['filter_choices'].append((i[0], url))

            available_filters.append(f_dict)
        return available_filters

    def get_selected_filter_objects(self):
        """
            Gets a list of tuples of selected filters and their selected items

            Example:
                [(<filter_object>, <item>),]
        """
        # cache for multiple calls
        if hasattr(self, '_selected_filter_list'):
            return self._selected_filter_list

        self._selected_filter_list = []
        # Cycle the GET parameters
        for param_key, value_list in self.request.GET.lists():
            # find the relevant filter
            for f in self.get_available_filters():
                if f.key == param_key:
                    for v in value_list:
                        if (f, v) not in self._selected_filter_list:
                            self._selected_filter_list.append((f, v))
                    break
        return self._selected_filter_list

    def get_selected_filter_querydict(self):
        """
            Get a querydict with just the selected filters. There may be other
            parameters in self.request.GET, so we want to remove thos
        """

        qd = QueryDict('')
        qd = qd.copy()
        d = {}
        selected_filters = self.get_selected_filter_objects()
        for filter, item in selected_filters:
            d[filter.key] = item
        qd.update(d)
        return qd

    def get_selected_filters_for_context(self):
        """
            Convert querydict to selected_filter list

                selected_filters = [{
                    'filter_title': <title>,
                    'selected_item_title': <selected_item_title>,
                    'del_link': <get_parameters> # a URL encoded link to this page w/out this filter
                    },]
        """
        filter_list = []

        # iterate through each GET param
        for f, v in self.get_selected_filter_objects():
            filter_list.append({
                'filter_title': f.title,
                'selected_item_title': f.get_active_title(v),
                'del_link': self.drop_filer_from_querydict(self.request.GET,
                                                           f.key,
                                                           v).urlencode()
            })

        return filter_list

    def remove_dupes(self, qd):
        """
            Removes any duplicate filters from the
        """
        pass

    def drop_filer_from_querydict(self, qd, filter_key, filter_value):
        """
            Returns the querydict with a filter removed
        """
        _qd = qd.copy()
        l = _qd.getlist(filter_key)

        if l and filter_value in l:

            l[:] = [x for x in l if x != filter_value]  # be sure to remove dupes
            _qd.setlist(filter_key, l)

            # if that was the only value, remove the key altogether
            if len(l) == 0:
                del _qd[filter_key]

        return _qd

    def add_filter_to_querydict(self, qd, filter_key, filter_value):
        """
            Returns a querydict with a filter added
        """
        _qd = qd.copy()
        l = _qd.getlist(filter_key)
        if l:
            l.append(filter_value)
            _qd.setlist(filter_key, l)
        else:
            _qd[filter_key] = filter_value

        return _qd


class NarrowFilteringMixin(FilteringMixin):
    """
        An extension of the FilteringMixin that removes filters from the
        available list of filters after they're used.

        It also provides a helper-function to display a queryset from all
        the selected filters.
    """

    def get_available_filters_for_context(self):
        """
            Removes a filter once it's in use
        """
        available_filters = super(NarrowFilteringMixin,
                                  self).get_available_filters_for_context()
        selected_filters = self.get_selected_filter_objects()
        for f in selected_filters:
            for af in available_filters:
                if af['filter_key'] == f[0].key:
                    available_filters.remove(af)
        return available_filters

    def get_filtered_queryset(self):
        """
            Compile all the selected filters into one queryset
        """
        qd = self.request.GET.copy()

        queryset_list = []

        for filter_key, selected_list in qd.lists():
            for filter in self.get_available_filters():
                if filter_key == filter.key:
                    for i in selected_list:
                        queryset_list.append(filter.get_results(i))

        qs = None
        if queryset_list:
            qs = queryset_list.pop()
            while queryset_list:
                next_qs = queryset_list.pop()
                qs = qs.filter(id__in=next_qs.values('id'))

        return qs
