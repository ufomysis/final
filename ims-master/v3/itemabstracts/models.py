from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.urls import reverse_lazy
from django.core.validators import RegexValidator
from utils.utils import upload_image_path, unique_slug_generator
from stdimage import StdImageField

USER = get_user_model()


class Unit(models.Model):
    title = models.CharField(max_length=60,
                             # validators=[
                             #     RegexValidator(
                             #         regex=NAME_REGEX,
                             #         message='ชื่อต้องประกอบด้วยตัวอักขระเท่านั้น'
                             #     )],
                             unique=True)
    added = models.DateTimeField(auto_now=False, auto_now_add=True)
    added_by = models.ForeignKey(USER, null=True, on_delete=models.SET_NULL, related_name='unit_added_by')

    class Meta:
        ordering = ['title', 'added']

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=60,
                             # validators=[
                             #     RegexValidator(
                             #         regex=NAME_REGEX,
                             #         message='ชื่อต้องประกอบด้วยตัวอักขระเท่านั้น'
                             #     )],
                             unique=True)
    added = models.DateTimeField(auto_now=False, auto_now_add=True)
    added_by = models.ForeignKey(USER, null=True, on_delete=models.SET_NULL, related_name='category_added_by')

    class Meta:
        ordering = ['title', 'added']

    def __str__(self):
        return self.title


ITEMABSTRACT_SERIAL_REGEX = '^[a-zA-Z0-9]{6}$'


class ItemAbstract(models.Model):
    title = models.CharField(max_length=60,
                             # validators=[
                             #     RegexValidator(
                             #         regex=NAME_REGEX,
                             #         message='ชื่อต้องประกอบด้วยตัวอักขระเท่านั้น'
                             #     )],
                             )
    serial = models.CharField(max_length=6,
                              validators=[
                                  RegexValidator(
                                      regex=ITEMABSTRACT_SERIAL_REGEX,
                                      message='หมายเลขแทนอุปกรณ์ต้องประกอบด้วยอักขระภาษาอังกฤษตัวพิมพ์ใหญ่หรือเล็กจำนวน 6 ตัว',
                                      code='invalid_serial'
                                  )],
                              unique=True)
    description = models.TextField(blank=True)
    image = StdImageField(upload_to=upload_image_path, blank=True, null=True,
                          delete_orphans=True,
                          )

    added = models.DateTimeField(auto_now=False, auto_now_add=True)
    added_by = models.ForeignKey(USER, null=True, on_delete=models.SET_NULL, related_name='itemabstract_added_by')
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(USER, null=True, on_delete=models.SET_NULL, related_name='itemabstract_updated_by')

    slug = models.SlugField(blank=True, unique=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='item_abstract_category')
    unit = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL, related_name='item_abstract_unit')
    allow_non_author_edit = models.BooleanField(default=False)
    track_1by1 = models.BooleanField(default=False)

    class Meta:
        ordering = ['title', 'serial']

    def get_absolute_url(self):
        return reverse_lazy("itemabstracts:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


def itemabstract_slug_serial(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    instance.serial = instance.serial.lower()


pre_save.connect(itemabstract_slug_serial, sender=ItemAbstract)
