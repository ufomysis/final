import django_filters

from .models import Branch


class BranchFilter(django_filters.FilterSet):

    class Meta:
        model = Branch
        fields = {
            'title': ['contains'],
            'alias': ['contains'],
            'address': ['contains'],

        }

    def __init__(self, *args, **kwargs):
       super(BranchFilter, self).__init__(*args, **kwargs)
       self.filters['title__contains'].label = 'ชื่อสาขา'
       self.filters['alias__contains'].label = 'รหัสสาขา'
       self.filters['address__contains'].label = 'ที่อยู่สาขา'




