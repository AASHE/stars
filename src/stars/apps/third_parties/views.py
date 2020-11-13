from django.views.generic import ListView

from logical_rules.mixins import RulesMixin

from models import ThirdParty

class SnapshotList(RulesMixin, ListView):

    template_name = "third_parties/snapshot_list.html"
    third_party = None

    def update_logical_rules(self):
        super(SnapshotList, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_can_access_third_party',
             'param_callbacks': [
                ('user', 'get_request_user'),
                ('third_party', 'get_tp_from_slug')
            ]
        })

    def get_tp_from_slug(self):
        if not self.third_party:
            self.third_party = ThirdParty.objects.get(slug=self.kwargs['slug'])
        return self.third_party

    def get_queryset(self):
        tp = self.get_tp_from_slug()
        return tp.get_snapshots().order_by("institution__name")

    def get_context_data(self, **kwargs):
        _context = super(SnapshotList, self).get_context_data(**kwargs)
        _context['third_party'] = self.get_tp_from_slug()
        return _context
