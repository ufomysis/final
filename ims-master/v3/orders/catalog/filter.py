import django_filters
from django import forms

from django.db.models import Q
from orders.models import Item, Branch, ItemLog, TransferRequest
from itemabstracts.models import Category
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, \
    YearPickerInput


ITEM_STATUS_CHOICES = (
    ('available', 'ว่าง'),
    ('unavailable', 'ไม่ว่าง'),
    ('reserved', 'จองแล้ว'),


)

class CatalogListFilter(django_filters.FilterSet):
    item_abstract__title = django_filters.CharFilter(lookup_expr='contains')
    item_abstract__category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    item_abstract__serial = django_filters.CharFilter(lookup_expr='contains')
    currently_at = django_filters.ModelChoiceFilter(queryset=Branch.objects.all())

    class Meta:
        model = Item
        fields = [

        ]

    def __init__(self, *args, **kwargs):
        super(CatalogListFilter, self).__init__(*args, **kwargs)

        self.filters['item_abstract__title'].label = 'ชื่ออุปกรณ์'
        self.filters['item_abstract__category'].label = 'ประเภท'
        self.filters['item_abstract__serial'].label = 'Serial Number'
        self.filters['currently_at'].label = 'อยู่ที่สาขา'



class CatalogDetailFilter(django_filters.FilterSet):
    tracking_number = django_filters.CharFilter(lookup_expr='contains')
    status = django_filters.ChoiceFilter(choices=ITEM_STATUS_CHOICES)

    class Meta:
        model = Item
        fields = [

        ]

    def __init__(self, *args, **kwargs):
        super(CatalogDetailFilter, self).__init__(*args, **kwargs)

        self.filters['tracking_number'].label = 'หมายเลขติดตาม'
        self.filters['status'].label = 'สถานะอุปกรณ์'


