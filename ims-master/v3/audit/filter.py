import django_filters
from django.db.models import Q
from .models import AuditForm, AuditSession, Branch

from bootstrap_datepicker_plus import DateTimePickerInput


class AuditFormFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='contains')
    description = django_filters.CharFilter(lookup_expr='contains')
    added_by = django_filters.CharFilter(method='user_', )

    class Meta:
        model = AuditForm
        fields = [

        ]

    def __init__(self, *args, **kwargs):
       super(AuditFormFilter, self).__init__(*args, **kwargs)
       self.filters['title'].label = 'ชื่อ'
       self.filters['description'].label = 'รายละเอียด'
       self.filters['added_by'].label = 'ผู้สร้าง'


    def user_(self, queryset, name, value):
        return queryset.filter(
            Q(added_by__username__icontains=value) |
            Q(added_by__email__icontains=value) |
            Q(added_by__first_name__icontains=value) |
            Q(added_by__last_name__icontains=value)
        ).distinct()



AUDITSESSION_STATUS_CHOICES = (
    ('in_progress', 'กำลังตรวจสอบ'),
    ('done', 'เสร็จสิ้น'),

)
class AuditSessionFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='contains')
    auditor = django_filters.CharFilter(method='user_', )
    branch = django_filters.ModelChoiceFilter(queryset=Branch.objects.all())
    status = django_filters.ChoiceFilter(choices=AUDITSESSION_STATUS_CHOICES)
    start_date = django_filters.DateTimeFilter('audit_date', lookup_expr="gte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))
    end_date = django_filters.DateTimeFilter('audit_date', lookup_expr="lte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))


    class Meta:
        model = AuditSession
        fields = [

        ]

    def __init__(self, *args, **kwargs):
        super(AuditSessionFilter, self).__init__(*args, **kwargs)
        self.filters['title'].label = 'ชื่อ'
        self.filters['auditor'].label = 'ผู้ตรวจสอบ'
        self.filters['branch'].label = 'สาขา'
        self.filters['status'].label = 'สถานะการตรวจสอบ'
        self.filters['start_date'].label = 'ตรวจสอบตั้งแต่วันที่'
        self.filters['end_date'].label = 'ตรวจสอบถึงวันที่'


    def user_(self, queryset, name, value):
        return queryset.filter(
            Q(added_by__username__icontains=value) |
            Q(added_by__email__icontains=value) |
            Q(added_by__first_name__icontains=value) |
            Q(added_by__last_name__icontains=value)
        ).distinct()

