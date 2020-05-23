import django_filters
from django.db.models import Q
from .models import Order
from bootstrap_datepicker_plus import DateTimePickerInput


ORDER_STATUS_CHOICES = (
    ('item_prepare', 'กำลังจัดเดรียมอุปกรณ์'),
    ('item_ready', 'พร้อมส่งมอบอุปกรณ์'),
    ('item_received', 'รับอุปกรณ์แล้ว'),
    ('item_returned', 'คืนอุปกรณ์แล้ว'),
    ('done', 'รายการเสร็จสิ้น'),
    ('canceled', 'รายการถูกยกเลิก'),
)
class OrderFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='contains')
    user = django_filters.CharFilter(method='user_', )
    status = django_filters.ChoiceFilter(choices=ORDER_STATUS_CHOICES)
    start_date = django_filters.DateTimeFilter('created_at', lookup_expr="gte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))
    end_date = django_filters.DateTimeFilter('created_at', lookup_expr="lte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))

    class Meta:
        model = Order
        fields = [
        ]

    def __init__(self, *args, **kwargs):
        super(OrderFilter, self).__init__(*args, **kwargs)
        self.filters['id'].label = 'รหัสรายการ'
        self.filters['user'].label = 'ผู้ขอเบิก'
        self.filters['status'].label = 'สถานะรายการ'
        self.filters['start_date'].label = 'สร้างรายการตั้งแต่วันที่'
        self.filters['end_date'].label = 'สร้างรายการถึงวันที่'

    def user_(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value)
        ).distinct()





