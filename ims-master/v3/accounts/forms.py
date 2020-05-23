from django.db.models import Q
from django import forms
from django.contrib.auth import get_user_model
from branches.models import Branch

USER = get_user_model()


class UserLoginForm(forms.Form):
    query = forms.CharField(label='ชื่อผู้ใช้ / Email')
    password = forms.CharField(label='รหัสผ่าน', widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        query = self.cleaned_data.get("query")
        password = self.cleaned_data.get("password")
        user_qs_final = USER.objects.filter(
            Q(username__iexact=query) |
            Q(email__iexact=query)
        ).distinct()
        if not user_qs_final.exists() and user_qs_final.count() != 1:
            raise forms.ValidationError("ไม่มีผู้ใช้นี้")
        user_obj = user_qs_final.first()
        if not user_obj.check_password(password):
            # log auth tries
            raise forms.ValidationError("รหัสผ่านไม่ถูกต้อง")
        self.cleaned_data["user_obj"] = user_obj

        return super(UserLoginForm, self).clean(*args, **kwargs)


USER_ACCOUNT_TYPE_CHOICES = (
    ('administrator', 'ผู้ดูแลระบบ'),
    ('normal', 'พนักงานทั่วไป'),
    ('inv_manager', 'ผู้ดูแลและจัดการอุปกรณ์'),
    ('auditor', 'ผู้ตรวจสอบอุปกรณ์'),
)


class UserCreateUpdateModelForm(forms.ModelForm):
    class Meta:
        model = USER
        fields = ('user_type', 'username', 'password', 'first_name', 'last_name', 'email', 'etc', 'image', 'branch')
        widgets = {
            'password': forms.PasswordInput(),
            'user_type': forms.Select(choices=USER_ACCOUNT_TYPE_CHOICES),

        }
        help_texts = {
            'username': 'ความยาวน้อยกว่า 150 ตัว และประกอบไปด้วยตัวอักขระ, เลข และตัวอักขระพิเศษ @/./+/-/_',
            'password': 'จะมีค่าเหมือนชื่อผู้ใช้หากไม่ระบุ',
            'etc': 'ความยาวน้อยกว่า 150 ตัว',
        }

        labels ={
            'user_type': 'ประเภทผู้ใช้',
            'username': 'ชื่อผู้ใช้',
            'password': 'รหัสผ่าน',
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล',
            'email': 'อีเมล์',
            'etc': 'ข้อมูลอื่นๆ',
            'image': 'รูปภาพ',
            'branch': 'สาขาที่ประจำอยู่',

        }


    def __init__(self, *args, **kwargs):
        super(UserCreateUpdateModelForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False

    def clean_username(self, *args, **kwargs):
        instance = self.instance
        username = self.cleaned_data.get('username')
        qs = USER.objects.filter(username__iexact=username)
        if instance is not None:
            qs = qs.exclude(username=instance.username)
        if qs.exists():
            raise forms.ValidationError("ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว")
        return username

    def clean_email(self, *args, **kwargs):
        instance = self.instance
        email = self.cleaned_data.get('email')
        qs = USER.objects.filter(email__iexact=email).exclude(email__iexact='')
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("อีเมล์นี้มีอยู่ในระบบแล้ว")
        return email



    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreateUpdateModelForm, self).save(commit=False)
        if not self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data["username"])
        else:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileUpdate(forms.ModelForm):
    class Meta:
        model = USER
        fields = ('first_name', 'last_name', 'email', 'etc', 'image')
        widgets = {

        }
        help_texts = {
            'etc': 'ความยาวน้อยกว่า 150 ตัว',
        }

        labels ={

            'etc': 'ข้อมูลอื่นๆ',
            'image': 'รูปภาพ',


        }

    def clean_email(self, *args, **kwargs):
        instance = self.instance
        email = self.cleaned_data.get('email')
        qs = USER.objects.filter(email__iexact=email).exclude(email__iexact='')
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("อีเมล์นี้มีอยู่ในระบบแล้ว")
        return email
