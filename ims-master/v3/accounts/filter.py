import django_filters
from django.contrib.auth import get_user_model
from .models import Branch



USER = get_user_model()

USER_ACCOUNT_TYPE_CHOICES = (
    ('administrator', 'ผู้ดูแลระบบ'),
    ('normal', 'ผู้ใช้งานทั่วไป'),
    ('inv_manager', 'ผู้ดูแลจัดการอุปกรณ์'),
    ('auditor', 'ผู้ตรวจสอบอุปกรณ์'),
)

class UserFilter(django_filters.FilterSet):
    user_type = django_filters.ChoiceFilter(choices=USER_ACCOUNT_TYPE_CHOICES)
    branch = django_filters.ModelChoiceFilter(queryset=Branch.objects.all())

    # field_order = ['user_type', 'new_password1', 'user_type']

    class Meta:
        model = USER
        fields = {
            'username': ['contains'],
            'email': ['contains'],
            'first_name': ['contains'],
            'last_name': ['contains'],

        }

    def __init__(self, *args, **kwargs):
       super(UserFilter, self).__init__(*args, **kwargs)
       self.filters['user_type'].label = 'ประเภทผู้ใช้งาน'
       self.filters['branch'].label = 'สาขา'
       self.filters['username__contains'].label = 'ชื่อผู้ใช้งาน'
       self.filters['email__contains'].label = 'E-mail'
       self.filters['first_name__contains'].label = 'ชื่อ'
       self.filters['last_name__contains'].label = 'นามสกุล'




