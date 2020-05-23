from django import forms
from .models import Unit, Category, ItemAbstract

class UnitCreateUpdateModelForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['title']
        labels = {
            'title': '',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'กรอกชื่อหน่วยนับที่ต้องการเพิ่มใหม่'})
        }

    def clean_title(self, *args, **kwargs):
        instance = self.instance
        title = self.cleaned_data.get('title')
        qs = Unit.objects.filter(title__iexact=title)

        if instance is not None:  #when update, it cant post the same title
            qs = qs.exclude(pk=instance.pk) # id=instance.id
        if qs.exists():
            raise forms.ValidationError("หน่วยนับนี้มีในระบบแล้ว")
        return title


class CategoryCreateUpdateModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title']
        labels = {
            'title': '',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'กรอกชื่อประเภทที่ต้องการเพิ่มใหม่'})
        }

    def clean_title(self, *args, **kwargs):
        instance = self.instance
        title = self.cleaned_data.get('title')
        qs = Unit.objects.filter(title__iexact=title)

        if instance is not None:  #when update, it cant post the same title
            qs = qs.exclude(pk=instance.pk) # id=instance.id
        if qs.exists():
            raise forms.ValidationError("ประเภทนี้มีในระบบแล้ว")
        return title



class ItemAbstractCreateForm(forms.ModelForm):

    class Meta:

        model = ItemAbstract
        fields = ['title', 'serial', 'description', 'image', 'category', 'unit', 'allow_non_author_edit', 'track_1by1']
        labels = {
            'title': 'ชื่ออุปกรณ์',
            'serial': 'รหัสอุปกรณ์',
            'description': 'คำอธิบายอุปกรณ์',
            'image': 'รูปภาพอุปกรณ์',
            'category': 'ประเภทอุปกรณ์',
            'unit': 'หน่วยนับอุปกรณ์',
            'allow_non_author_edit': 'อนุญาตให้ผู้อื่นแก้ไขข้อมูลได้',
            'track_1by1': 'เพิ่มหมายเลขติดตามอุปกรณ์ทุกชิ้น',
        }
        help_texts = {
            'serial': 'หมายเลขแทนอุปกรณ์ต้องประกอบด้วยอักขระภาษาอังกฤษตัวพิมพ์ใหญ่หรือเล็กจำนวน 5 ตัว',
            'allow_non_author_edit': 'อนุญาตให้ผู้ดูแลอุปกรณ์คนอื่นแก้ไขและลบข้อมูลได้',
            'track_1by1': 'ปล่อยว่างในกรณีที่อุปกรณ์เป็นของใช้สิ้นเปลืองและไม่ต้องการรับคืน เช่น กระดาษ, เครื่องเขียนและอื่นๆ',
        }



    def clean_serial(self, *args, **kwargs):
        instance = self.instance
        serial = self.cleaned_data.get('serial')
        qs = ItemAbstract.objects.filter(serial__iexact=serial)

        if instance is not None:  #when update, it cant post the same title
            qs = qs.exclude(pk=instance.pk) # id=instance.id
        if qs.exists():
            raise forms.ValidationError("This serial has already been used. Please try again.")
        return serial


class ItemAbstractUpdateForm(forms.ModelForm):

    class Meta:

        model = ItemAbstract
        fields = ['title', 'serial', 'description', 'image', 'category', 'unit', 'allow_non_author_edit']
        labels = {
            'title': 'ชื่ออุปกรณ์',
            'serial': 'รหัสอุปกรณ์',
            'description': 'คำอธิบายอุปกรณ์',
            'image': 'รูปภาพอุปกรณ์',
            'category': 'ประเภทอุปกรณ์',
            'unit': 'หน่วยนับอุปกรณ์',
            'allow_non_author_edit': 'อนุญาตให้ผู้อื่นแก้ไขข้อมูลได้'
        }

        help_texts = {
            'serial': 'หมายเลขแทนอุปกรณ์ต้องประกอบด้วยอักขระภาษาอังกฤษตัวพิมพ์ใหญ่หรือเล็กจำนวน 5 ตัว',
            'allow_non_author_edit': 'อนุญาตให้ผู้ดูแลอุปกรณ์คนอื่นแก้ไขและลบข้อมูลได้',
        }

    def clean_serial(self, *args, **kwargs):
        instance = self.instance
        serial = self.cleaned_data.get('serial')
        qs = ItemAbstract.objects.filter(serial__iexact=serial)

        if instance is not None:  #when update, it cant post the same title
            qs = qs.exclude(pk=instance.pk) # id=instance.id
        if qs.exists():
            raise forms.ValidationError("This serial has already been used. Please try again.")
        return serial

