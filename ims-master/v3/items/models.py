from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.urls import reverse_lazy
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Q

import uuid

from utils.utils import auto_tracking_number
from itemabstracts.models import ItemAbstract
from branches.models import Branch

USER = get_user_model()

ITEM_STATUS_CHOICES = (
    ('info', 'info'),
    ('available', 'available'),
    ('lost', 'LOST'),
    ('unavailable', 'unavailable'),
    ('reserved', 'reserved'),
    ('requested_to_be_transfered', 'requested_to_be_transfered'),
    ('preparing_for_shipment', 'preparing_for_shipment'),
    ('shipping', 'SHIPPING'),

)


class ItemQuerySet(models.query.QuerySet):

    def get_registered(self, item_abstract, currently_at):
        return self.filter(item_abstract=item_abstract, currently_at=currently_at, status='info')

    def get_track_1by1_items_info(self):  ##
        return self.filter(item_abstract__track_1by1=True, status='info')

    def get_track_1_items_info(self):  ##
        return self.filter(item_abstract__track_1by1=False, status='info')

    def get_all_list_ver(self):
        track_1by1_items = self.get_track_1by1_items_info()
        track_1 = self.get_track_1_items_info()
        qs = (track_1by1_items | track_1).distinct()
        return qs

    def get_all_current_branch_only_list_ver(self, currently_at_slug):
        return self.get_all_list_ver().filter(currently_at__slug=currently_at_slug)

    def get_by_iabstract_slug_currently_at_slug_detail_ver(self, iabstract_slug, currently_at_slug):
        track_1by1 = self.filter(
            item_abstract__slug=iabstract_slug, currently_at__slug=currently_at_slug, item_abstract__track_1by1=True
        ).exclude(status='info')
        no_track = self.filter(
            item_abstract__slug=iabstract_slug, currently_at__slug=currently_at_slug, item_abstract__track_1by1=False
        ).filter(
            Q(status='available') |
            Q(status='unavailable')
        )
        return (track_1by1 | no_track).distinct()

    def get_by_serial_no_info(self, serial):
        return self.filter(item_abstract__serial=serial).exclude(status='info').exclude(status='reserved').exclude(
            status='shipping')

    def get_by_serial_no_info_this_branch(self, serial, branch__slug):
        return self.filter(item_abstract__serial=serial, currently_at=branch__slug).exclude(status='info')

    def get_by_serial_with_info(self, serial):
        return self.filter(item_abstract__serial=serial)

    def get_by_serial_with_info_this_branch(self, serial, branch__slug):
        return self.filter(item_abstract__serial=serial, currently_at=branch__slug)

    def get_by_status(self, serial, status):
        return self.filter(item_abstract__serial=serial, status=status)

    def get_by_status_this_branch(self, serial, status, branch):
        return self.filter(item_abstract__serial=serial, status=status, currently_at=branch)


class ItemManager(models.Manager):
    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db)

    def get_registered(self, item_abstract, currently_at):
        return self.get_queryset().get_registered(item_abstract, currently_at)

    def get_all_list_ver(self):
        return self.get_queryset().get_all_list_ver()

    def get_all_current_branch_only_list_ver(self, currently_at_slug):
        return self.get_queryset().get_all_current_branch_only_list_ver(currently_at_slug)

    def get_by_iabstract_slug_currently_at_slug_detail_ver(self, iabstract_slug, currently_at_slug):
        return self.get_queryset().get_by_iabstract_slug_currently_at_slug_detail_ver(iabstract_slug, currently_at_slug)

    def get_by_serial_no_info(self, serial):
        return self.get_queryset().get_by_serial_no_info(serial)

    def get_by_serial_no_info_this_branch(self, serial, branch__slug):
        return self.get_queryset().get_by_serial_no_info_this_branch(serial, branch__slug)

    def get_by_serial_with_info(self, serial):
        return self.get_queryset().get_by_serial_with_info(serial)

    def get_by_serial_with_info_this_branch(self, serial, branch__slug):
        return self.get_queryset().get_by_serial_with_info_this_branch(serial, branch__slug)

    def get_by_status(self, serial, status):
        return self.get_queryset().get_by_status(serial, status)

    def get_by_status_this_branch(self, serial, status, branch):
        return self.get_queryset().get_by_status_this_branch(serial, status, branch)


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_abstract = models.ForeignKey(ItemAbstract, on_delete=models.CASCADE, related_name='item')
    status = models.CharField(max_length=30, default='available', choices=ITEM_STATUS_CHOICES)
    tracking_number = models.PositiveIntegerField(blank=True)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    currently_at = models.ForeignKey(Branch, on_delete=models.CASCADE,
                                     related_name='item_currently_at')

    objects = ItemManager()

    class Meta:
        ordering = ('currently_at', 'item_abstract__serial', '-tracking_number')

    def __str__(self):
        return self.item_abstract.serial + '-' + str(self.tracking_number)

    def get_absolute_url(self):
        return reverse_lazy("items:detail", kwargs={"serial": self.item_abstract.serial})

    @staticmethod
    def is_registered(item_abstract, currently_at):
        check_inv = Item.objects.get_registered(item_abstract, currently_at)

        if check_inv.count() > 0:
            return True
        return False

    @staticmethod
    def register(item_abstract, currently_at):
        if item_abstract.track_1by1:

            new_info = Item.objects.create(item_abstract=item_abstract, currently_at=currently_at, status='info',
                                           quantity=0,
                                           tracking_number=0)
        else:
            new_info = Item.objects.create(item_abstract=item_abstract, currently_at=currently_at, status='info',
                                           quantity=0,
                                           tracking_number=0)
            new_item = Item.objects.create(item_abstract=item_abstract, currently_at=currently_at, status='available',
                                           quantity=0,
                                           tracking_number=1)
            Item.objects.create(item_abstract=item_abstract, currently_at=currently_at, status='reserved',
                                quantity=0,
                                tracking_number=10)
            Item.objects.create(item_abstract=item_abstract, currently_at=currently_at, status='shipping',
                                quantity=0,
                                tracking_number=11)

        return new_info

    def deregister(self):
        del_info = self
        self.delete()
        return del_info

    @staticmethod
    def get_info_obj(item_abstract_slug, currently_at_slug):
        info_qs = Item.objects.filter(item_abstract__slug=item_abstract_slug, currently_at__slug=currently_at_slug,
                                      status='info')

        return info_qs.first()

    @staticmethod
    def get_info_obj_by_id(id):
        info_qs = Item.objects.filter(id=id)

        return info_qs.first()

    @staticmethod
    def get_qs_by_info_id(id):
        info_obj = Item.get_info_obj_by_id(id)
        if info_obj.item_abstract.track_1by1:
            qs = Item.objects.filter(
                Q(item_abstract=info_obj.item_abstract, currently_at=info_obj.currently_at, status='available') |
                Q(item_abstract=info_obj.item_abstract, currently_at=info_obj.currently_at, status='unavailable') |
                Q(item_abstract=info_obj.item_abstract, currently_at=info_obj.currently_at, status='reserved')
            ).distinct()
        else:
            qs = Item.objects.filter(
                Q(item_abstract=info_obj.item_abstract, currently_at=info_obj.currently_at, status='available') |
                Q(item_abstract=info_obj.item_abstract, currently_at=info_obj.currently_at, status='unavailable')
            ).distinct()
        return qs

    def get_q_all_branches(self):
        if self.item_abstract.track_1by1:

            q_all = Item.objects.get_by_serial_no_info(self.item_abstract.serial).count()
            q_available = Item.objects.get_by_status(self.item_abstract.serial, 'available').count()
            q_unavailable = Item.objects.get_by_status(self.item_abstract.serial, 'unavailable').count()
            q_reserved = Item.objects.get_by_status(self.item_abstract.serial, 'reserved').count()

            requested_to_be_transfered = Item.objects.get_by_status(self.item_abstract.serial,
                                                                    'requested_to_be_transfered')
            preparing_for_shipment = Item.objects.get_by_status(self.item_abstract.serial,
                                                                'preparing_for_shipment')
            shipping = Item.objects.get_by_status(self.item_abstract.serial, 'shipping')
            q_shipping_process = (requested_to_be_transfered | preparing_for_shipment | shipping).distinct().count()

            q = {
                'all': q_all,
                'available': q_available,
                'unavailable': q_unavailable,
                'reserved': q_reserved,
                'shipping_process': q_shipping_process,
            }

        else:
            all_items = Item.objects.get_by_serial_with_info(self.item_abstract.serial)
            available_items = Item.objects.get_by_status(self.item_abstract.serial, 'available')
            reserved_items = Item.objects.get_by_status(self.item_abstract.serial, 'reserved')
            shipping_items = Item.objects.get_by_status(self.item_abstract.serial, 'shipping')

            q = {}

            temp_q = 0
            for item in all_items:
                temp_q += item.quantity
            q['all'] = temp_q

            temp_q = 0
            for item in available_items:
                temp_q += item.quantity
            q['available'] = temp_q

            temp_q = 0
            for item in reserved_items:
                temp_q += item.quantity
            q['reserved'] = temp_q

            temp_q = 0
            for item in shipping_items:
                temp_q += item.quantity
            q['shipping_process'] = temp_q
        return q

    def get_q_this_branch(self):
        if self.item_abstract.track_1by1:

            q_all = Item.objects.get_by_serial_no_info_this_branch(self.item_abstract.serial,
                                                                   self.currently_at).count()
            q_available = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'available',
                                                                 self.currently_at).count()

            q_unavailable = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'unavailable',
                                                                   self.currently_at).count()
            q_reserved = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'reserved',
                                                                self.currently_at).count()

            requested_to_be_transfered = Item.objects.get_by_status_this_branch(self.item_abstract.serial,
                                                                                'requested_to_be_transfered',
                                                                                self.currently_at)
            preparing_for_shipment = Item.objects.get_by_status_this_branch(self.item_abstract.serial,
                                                                            'preparing_for_shipment',
                                                                            self.currently_at)
            shipping = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'shipping',
                                                              self.currently_at)
            q_shipping_process = (requested_to_be_transfered | preparing_for_shipment | shipping).distinct().count()

            q = {
                'all': q_all,
                'available': q_available,
                'unavailable': q_unavailable,
                'reserved': q_reserved,
                'shipping_process': q_shipping_process,
            }

        else:
            q = {}
            all_items = Item.objects.get_by_serial_with_info_this_branch(self.item_abstract.serial, self.currently_at)
            available_items = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'available',
                                                                     self.currently_at)
            reserved_items = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'reserved',
                                                                    self.currently_at)
            shipping_items = Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'shipping',
                                                                    self.currently_at)
            temp_q = 0
            for item in all_items:
                temp_q += item.quantity
            q['all'] = temp_q

            temp_q = 0
            for item in available_items:
                temp_q += item.quantity
            q['available'] = temp_q

            temp_q = 0
            for item in reserved_items:
                temp_q += item.quantity
            q['reserved'] = temp_q

            temp_q = 0
            for item in shipping_items:
                temp_q += item.quantity
            q['shipping_process'] = temp_q
        return q

    def is_empty_inv(self):

        test_get_no_info = Item.objects.get_by_serial_no_info_this_branch(self.item_abstract.serial,
                                                                          self.currently_at)
        if not self.item_abstract.track_1by1:
            for item in test_get_no_info:
                if item.quantity > 0:
                    return False
            return True

        count = test_get_no_info.count()
        return count == 0

    def increase_quantity(self, increase_by):
        if self.item_abstract.track_1by1:
            new_items = []
            new_tracking_number = 0
            for i in range(increase_by):
                new_item = Item(item_abstract=self.item_abstract, quantity=1, currently_at=self.currently_at)

                if i == 0:
                    new_tracking_number = auto_tracking_number(new_item, self.item_abstract.serial)
                else:
                    new_tracking_number += 1

                new_item.tracking_number = new_tracking_number
                new_items.append(new_item)
            Item.objects.bulk_create(new_items)
        else:
            available_item = (
                    Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'available',
                                                           self.currently_at) |
                    Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'unavailable',
                                                           self.currently_at)
            ).distinct()
            if available_item.count() == 0:
                new_non_track_item = Item.objects.create(item_abstract=self.item_abstract, quantity=increase_by,
                                                         currently_at=self.currently_at, tracking_number=1)
            else:
                item = available_item.first()
                item.quantity += increase_by
                item.save()


    def decrease_quantity(self, decrease_by):

        if self.item_abstract.track_1by1:
            to_del = Item.objects.filter(item_abstract=self.item_abstract, status='available').order_by(
                '-tracking_number')[:-decrease_by].values_list("id", flat=True)
            Item.objects.filter(id__in=list(to_del)).delete()

        else:
            available_item = (
                Item.objects.get_by_status_this_branch(self.item_abstract.serial, 'available',
                                                       self.currently_at)
            ).distinct()

            item = available_item.first()

            item.quantity += decrease_by
            item.save()


def track1_out_of_stock_watcher(sender, instance, *args, **kwargs):
    if not instance.item_abstract.track_1by1:
        if instance.quantity <= 0 and (
                instance.status != 'info' and instance.status != 'reserved' and instance.status != 'shipping'):
            instance.status = 'unavailable'
        else:
            if instance.status == 'unavailable':
                instance.status = 'available'


pre_save.connect(track1_out_of_stock_watcher, sender=Item)

ITEMLOG_EVENT_CHOICES = (
    ('ลงทะเบียนข้อมูลอุปกรณ์ใหม่', 'ลงทะเบียนข้อมูลอุปกรณ์ใหม่'),
    ('ลบข้อมูลอุปกรณ์ออกจากคลังสาขา', 'ลบข้อมูลอุปกรณ์ออกจากคลังสาขา'),
    ('ขนย้ายอุปกรณ์ระหว่างสาขา', 'ขนย้ายอุปกรณ์ระหว่างสาขา'),
    ('เปลี่ยนแปลงจำนวนอุปกรณ์ในคลังสาขา', 'เปลี่ยนแปลงจำนวนอุปกรณ์ในคลังสาขา'),

)


class ItemLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial = models.CharField(max_length=30)
    event_note = models.CharField(max_length=150, blank=True)
    user_comment = models.CharField(max_length=150, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    related_user = models.ForeignKey(USER, null=True, blank=True, on_delete=models.SET_NULL)
    related_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-timestamp', 'serial')

    @staticmethod
    def t_req_log(klass_obj, user, status, amount=0, **kwargs):
        serial = klass_obj.item.item_abstract.slug
        user_comment = ''
        if kwargs['related_order'] is not None:
            user_comment = f"เลขรายการยืม {kwargs['related_order'].id}"
        event_note = f"{status} | ชื่อ: {klass_obj.item.item_abstract.title} รหัส: {serial} หมายเลขติดตาม: {klass_obj.item.tracking_number} " \
            f"จำนวน {klass_obj.amount} {klass_obj.item.item_abstract.unit.title} " \
            f"จาก: {klass_obj.src_branch.title} " \
            f"ไปยัง: {klass_obj.dst_branch.title} " \
            f"โดย: {user.username}"
        timestamp = timezone.now()
        related_user = user
        related_branch = user.branch

        ItemLog.objects.create(serial=serial, event_note=event_note, user_comment=user_comment,
                               timestamp=timestamp,
                               related_user=related_user, related_branch=related_branch)

    @staticmethod
    def generate_log(klass_obj, user, log_type, amount=0, **kwargs):
        klassname = klass_obj.__class__.__name__
        if klassname == 'TransferRequest':

            if log_type == 'dispatched':
                ItemLog.t_req_log(klass_obj, user, status='เริ่มขนย้ายอุปกรณ์', amount=0, **kwargs)

            elif log_type == 'received':
                ItemLog.t_req_log(klass_obj, user, status='รับเข้าอุปกรณ์', amount=0, **kwargs)

            elif log_type == 'request_sent':
                ItemLog.t_req_log(klass_obj, user, status='ส่งคำขออนุญาตการขนย้าย', amount=0, **kwargs)

            elif log_type == 'request_accepted':
                ItemLog.t_req_log(klass_obj, user, status='ตอบรับคำขออนุญาตการขนย้าย', amount=0, **kwargs)

            elif log_type == 'canceled':
                ItemLog.t_req_log(klass_obj, user, status='ยกเลิกคำขออนุญาตการขนย้าย', amount=0, **kwargs)




        elif klassname == 'Item':
            if log_type == 'register_item':
                serial = klass_obj.item_abstract.slug
                event_note = f"ลงทะเบียนอุปกรณ์ | ชื่อ: {klass_obj.item_abstract.title} รหัส: {serial} " \
                    f"สู่คลังสาขา: {klass_obj.currently_at} โดย: {user.username}"
                user_comment = ''
                timestamp = timezone.now()
                related_user = user
                related_branch = user.branch

                ItemLog.objects.create(serial=serial, event_note=event_note, user_comment=user_comment,
                                       timestamp=timestamp,
                                       related_user=related_user, related_branch=related_branch)

            elif log_type == 'deregister_item':
                serial = klass_obj.item_abstract.slug
                event_note = f"ลบข้อมูลอุปกรณ์ | ชื่อ: {klass_obj.item_abstract.title} รหัส: {serial} " \
                    f"ออกจากคลังสาขา: {klass_obj.currently_at} โดย: {user.username}"
                user_comment = ''
                timestamp = timezone.now()
                related_user = user
                related_branch = user.branch

                ItemLog.objects.create(serial=serial, event_note=event_note, user_comment=user_comment,
                                       timestamp=timestamp,
                                       related_user=related_user, related_branch=related_branch)

            elif log_type == 'increase_q':
                serial = klass_obj.item_abstract.slug
                event_note = f"เพิ่มจำนวนอุปกรณ์ | ชื่อ: {klass_obj.item_abstract.title} รหัส: {serial} " \
                    f"จำนวน {amount} {klass_obj.item_abstract.unit.title} โดย: {user.username}"

                user_comment = ''
                timestamp = timezone.now()
                related_user = user
                related_branch = user.branch

                ItemLog.objects.create(serial=serial, event_note=event_note, user_comment=user_comment,
                                       timestamp=timestamp,
                                       related_user=related_user, related_branch=related_branch)

            elif log_type == 'decrease_q':
                serial = klass_obj.item_abstract.slug
                event_note = f"ลดจำนวนอุปกรณ์ | ชื่อ: {klass_obj.item_abstract.title} รหัส: {serial} " \
                    f"จำนวน {amount} {klass_obj.item_abstract.unit.title} โดย: {user.username}"

                user_comment = ''
                timestamp = timezone.now()
                related_user = user
                related_branch = user.branch

                ItemLog.objects.create(serial=serial, event_note=event_note, user_comment=user_comment,
                                       timestamp=timestamp,
                                       related_user=related_user, related_branch=related_branch)
