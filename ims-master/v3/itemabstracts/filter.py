import django_filters

from .models import Unit, Category, ItemAbstract


class UnitFilter(django_filters.FilterSet):
    class Meta:
        model = Unit
        fields = {
            'title': ['contains'],
        }

    def __init__(self, *args, **kwargs):
        super(UnitFilter, self).__init__(*args, **kwargs)
        self.filters['title__contains'].label = 'ชื่อหน่วยนับ'


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = {
            'title': ['contains'],
        }

    def __init__(self, *args, **kwargs):
        super(CategoryFilter, self).__init__(*args, **kwargs)
        self.filters['title__contains'].label = 'ชื่อประเภท'


class ItemAbstractFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all()
    )

    class Meta:
        model = ItemAbstract
        fields = {
            'title': ['contains'],
            'serial': ['contains'],
        }

    def __init__(self, *args, **kwargs):
        super(ItemAbstractFilter, self).__init__(*args, **kwargs)
        self.filters['title__contains'].label = 'ชื่ออุปกรณ์'
        self.filters['serial__contains'].label = 'รหัสอุปกรณ์'
        self.filters['category'].label = 'ประเภทอุปกรณ์'
