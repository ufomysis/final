import django_filters

from django.db.models import Q
from orders.models import Item, Branch, ItemLog, TransferRequest
from itemabstracts.models import Category
from bootstrap_datepicker_plus import DateTimePickerInput



class SerialFilter(django_filters.FilterSet):
    item_abstract__title = django_filters.CharFilter(lookup_expr='contains')
    item_abstract__category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    item_abstract__serial = django_filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = Item
        fields = [
        ]

    def __init__(self, *args, **kwargs):
        super(SerialFilter, self).__init__(*args, **kwargs)
        self.filters['item_abstract__title'].label = 'ชื่ออุปกรณ์'
        self.filters['item_abstract__category'].label = 'ประเภท'
        self.filters['item_abstract__serial'].label = 'Serial Number'



class LogFilter(django_filters.FilterSet):
    serial = django_filters.CharFilter(lookup_expr='contains')
    event_comment = django_filters.CharFilter(method='event_comment_search', )
    related_user = django_filters.CharFilter(method='user_', )
    related_branch = django_filters.ModelChoiceFilter(queryset=Branch.objects.all())
    start_date = django_filters.DateTimeFilter('timestamp', lookup_expr="gte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))
    end_date = django_filters.DateTimeFilter('timestamp', lookup_expr="lte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))

    class Meta:
        model = ItemLog
        fields = [
        ]

    def event_comment_search(self, queryset, name, value):
        return queryset.filter(
            Q(event_note__icontains=value) |
            Q(user_comment__icontains=value)
        ).distinct()

    def user_(self, queryset, name, value):
        return queryset.filter(
            Q(related_user__username__icontains=value) |
            Q(related_user__email__icontains=value) |
            Q(related_user__first_name__icontains=value) |
            Q(related_user__last_name__icontains=value)
        ).distinct()

    def __init__(self, *args, **kwargs):
        super(LogFilter, self).__init__(*args, **kwargs)

        self.filters['serial'].label = 'Serial Number'
        self.filters['event_comment'].label = 'เหตุการณ์หรือหมายเหตุ'
        self.filters['related_user'].label = 'ผู้เกี่ยวข้องในการจัดการ'
        self.filters['related_branch'].label = 'สาขา'
        self.filters['start_date'].label = 'ตั้งแต่วันที่'
        self.filters['end_date'].label = 'ถึงวันที่'


class T_Request_Filter(django_filters.FilterSet):
    src_branch = django_filters.ModelChoiceFilter(queryset=Branch.objects.all())
    dst_branch = django_filters.ModelChoiceFilter(queryset=Branch.objects.all())
    req_staff = django_filters.CharFilter(method='req_staff_search', )
    item = django_filters.CharFilter(method='item_search', )
    ref_order__id = django_filters.CharFilter(lookup_expr='contains')
    start_date = django_filters.DateTimeFilter('timestamp', lookup_expr="gte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))
    end_date = django_filters.DateTimeFilter('timestamp', lookup_expr="lte", widget=DateTimePickerInput(
        options={
            "locale": "th",
        }
    ))

    class Meta:
        model = TransferRequest
        fields = [

        ]

    def __init__(self, *args, **kwargs):
        super(T_Request_Filter, self).__init__(*args, **kwargs)

        self.filters['src_branch'].label = 'สาขาต้นทาง'
        self.filters['dst_branch'].label = 'สาขาปลายทาง'
        self.filters['req_staff'].label = 'ผู้เกี่ยวข้องในการจัดการ'
        self.filters['item'].label = 'อุปกรณ์'
        self.filters['ref_order__id'].label = 'หมายเลขรายการเบิกที่เกี่ยวข้อง'
        self.filters['start_date'].label = 'ตั้งแต่วันที่'
        self.filters['end_date'].label = 'ถึงวันที่'


    def req_staff_search(self, queryset, name, value):
        return queryset.filter(
            Q(req_sender__username__icontains=value) |
            Q(req_sender__email__icontains=value) |
            Q(req_sender__first_name__icontains=value) |
            Q(req_sender__last_name__icontains=value) |
            Q(req_receiver__username__icontains=value) |
            Q(req_receiver__email__icontains=value) |
            Q(req_receiver__first_name__icontains=value) |
            Q(req_receiver__last_name__icontains=value)

        ).distinct()

    def item_search(self, queryset, name, value):
        return queryset.filter(
            Q(item__item_abstract__title__icontains=value) |
            Q(item__item_abstract__serial__icontains=value) |
            Q(item__item_abstract__category__title__icontains=value) |
            Q(item__tracking_number__icontains=value)

        ).distinct()