from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse_lazy
from utils.utils import unique_slug_generator
from django.core.validators import RegexValidator
from utils.utils import upload_image_path
from stdimage import StdImageField

BRANCH_ALIAS_REGEX = '^[a-zA-Z0-9]{6}$'


class Branch(models.Model):
    title = models.CharField(max_length=60,
                             unique=True,
                             error_messages={
                                 'unique': 'ชื่อสาขาที่ระบุซ้ำกับชื่อสาขาอื่นในระบบ',

                             },
                             # validators=[
                             #     RegexValidator(
                             #         regex=NAME_REGEX,
                             #         message='ชื่อต้องประกอบด้วยตัวอักขระเท่านั้น'
                             #     )],
                             )
    alias = models.CharField(max_length=6,
                             validators=[
                                 RegexValidator(
                                     regex=BRANCH_ALIAS_REGEX,
                                     message='รหัสสาขาต้องประกอบด้วยตัวเลขหรืออักขระภาษาอังกฤษตัวพิมพ์ใหญ่หรือเล็กจำนวน 6 ตัว',
                                     code='invalid_alias'
                                 )],
                             unique=True)
    address = models.TextField(blank=True)
    image = StdImageField(upload_to=upload_image_path, blank=True, null=True,
                          delete_orphans=True,
                          )
    slug = models.SlugField(blank=True, unique=True, editable=False)

    class Meta:
        ordering = ['alias', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy("branches:branch_detail", kwargs={"branch_slug": self.slug})


def branch_slug_alias(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
    instance.alias = instance.alias.lower()


pre_save.connect(branch_slug_alias, sender=Branch)
