from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.urls import reverse_lazy
from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.mail import send_mail

from django.utils import timezone
from django.db.models import Q
import uuid


from items.models import Item, Branch, ItemLog

USER = get_user_model()

ORDER_STATUS_CHOICES = (
    ('created', 'CREATED'),
    ('wait_t_confirm', 'wait_t_confirm'),
    ('item_prepare', 'PREPARING'),
    ('item_ready', 'READY'),
    ('item_received', 'ITEM_RECEIVED'),
    ('item_returned', 'item_returned'),
    ('overdue', 'OVERDUE'),
    ('done', 'DONE'),
    ('canceled', 'CANCELED'),
)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(USER, null=True, blank=True, on_delete=models.SET_NULL, related_name='order_user')
    inv_manager = models.ForeignKey(USER, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='order_inv_manager')
    items = models.ManyToManyField(Item, blank=True, through='Order_Item', related_name='orders')
    note = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)

    class Meta:
        ordering = ('-updated_at', '-created_at')

    def get_absolute_url(self):
        return reverse_lazy("orders:detail", kwargs={"pk": self.id})


    def send_mail(self, noti_type, request_user=None):
        if self.user.email:
            current_site = settings.SITE_URL

            items_list = 'รายการอุปกรณ์\n'
            for order_item in self.order_item_order.all():
                items_list += f'ชื่ออุปกรณ์: {order_item.item.item_abstract.title} ' \
                    f'serial: {order_item.item.item_abstract.serial} ' \
                    f'หมายเลขติดตาม: {order_item.item.tracking_number} ' \
                    f'จำนวน: {order_item.amount} {order_item.item.item_abstract.unit.title}\n'

            body = f'รายการยืมหมายเลข {self.id}\n'

            if noti_type == 'created':
                title = f'New Order Created # {self.id}'
                body += 'สร้างรายกายเบิกใหม่แล้ว\n'
            if noti_type == 'canceled':
                title = f'Order Canceled # {self.id}'
                body+=f'ถูกยกเลิกโดย {request_user.username}\n'
                self.note = f'ถูกยกเลิกโดย {request_user.username}\n'
                self.save()
            if noti_type == 'item_ready':
                title = f'Your Order is Ready # {self.id}'
                body+='กรุณารับอุปกรณ์ที่สาขาของท่าน \n'
            if noti_type == 'done':
                title = f'Order Completed # {self.id}'
                body+='รายการเบิกเสร็จสิ้น\n'

            body += items_list
            body += f'รายละเอียดเพิ่มเติม {current_site}orders/{self.id}'

            send_mail(title, body, 'admin@ims.com', [self.user.email, ])


    def shipping_needed(self):
        order_item_s = self.order_item_order.all()

        return order_item_s.first().item.currently_at != self.user.branch

    def reserve_items_in_order(self):
        order_item_s = self.order_item_order.all()
        sample_item = order_item_s.first().item
        i_abstract = sample_item.item_abstract
        current_branch = sample_item.currently_at
        reserved_obj = Item.objects.filter(item_abstract=i_abstract, currently_at=current_branch,
                                           status='reserved').first()

        for order_item in order_item_s:
            if order_item.item.item_abstract.track_1by1:

                order_item.item.status = 'reserved'
                order_item.item.save()
            else:

                reserved_obj.quantity += order_item.amount
                reserved_obj.save()

                order_item.item.quantity -= order_item.amount
                order_item.item.save()


    def restore_items(self, current_branch):
        order_item_s = self.order_item_order.all()

        sample_item = order_item_s.first().item
        i_abstract = sample_item.item_abstract

        for order_item in order_item_s:


            if order_item.item.item_abstract.track_1by1:

                order_item.item.status = 'available'
                order_item.item.save()
            else:
                reserved_obj = Item.objects.filter(item_abstract=i_abstract, currently_at=current_branch,
                                                   status='reserved').first()
                reserved_obj.quantity -= order_item.amount
                reserved_obj.save()

                item = Item.objects.filter(
                    Q(item_abstract=i_abstract, currently_at=current_branch, status='available') |
                    Q(item_abstract=i_abstract, currently_at=current_branch, status='unavailable')
                ).distinct().first()

                item.quantity += order_item.amount
                item.save()



    def make_items_unavailable(self):
        order_item_s = self.order_item_order.all()

        for order_item in order_item_s:
            if order_item.item.item_abstract.track_1by1:
                order_item.item.status = 'unavailable'
                order_item.item.save()






class Order_Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_item_item')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_item_order')
    amount = models.IntegerField(validators=[MinValueValidator(1)], default=1)




class OrderStatusTimestamp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    related_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_status_timestamp')
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15)

    class Meta:
        unique_together = ['related_order', 'status']

    @staticmethod
    def stamp(related_order, status):
        status_timestamp_obj, status_timestamp_created = OrderStatusTimestamp.objects.get_or_create(
            related_order=related_order, status=status)
        if not status_timestamp_created:
            status_timestamp_obj.save()

    @staticmethod
    def get_status_timestamps(related_order):
        all_stamps = related_order.order_status_timestamp.all()
        created = all_stamps.filter(status='created').first()
        item_prepare = all_stamps.filter(status='item_prepare').first()
        item_ready = all_stamps.filter(status='item_ready').first()
        item_received = all_stamps.filter(status='item_received').first()
        item_returned = all_stamps.filter(status='item_returned').first()
        overdue = all_stamps.filter(status='overdue').first()
        done = all_stamps.filter(status='done').first()
        canceled = all_stamps.filter(status='canceled').first()

        q = {
            'created': created,
            'item_prepare': item_prepare,
            'item_ready': item_ready,
            'item_received': item_received,
            'item_returned': item_returned,
            'overdue': overdue,
            'done': done,
            'canceled': canceled,

        }

        return q


def change_order_status(sender, instance, *args, **kwargs):
    test_get_order_req = Order.objects.filter(id=instance.id)

    if test_get_order_req.count() > 0:
        pre_save_status = Order.objects.get(id=instance.id).status

        is_saving_status = instance.status

        if pre_save_status != is_saving_status:
            instance.updated_at = timezone.now()
            if is_saving_status == 'created':
                instance.send_mail('created')
                OrderStatusTimestamp.stamp(instance, 'created')

                instance.reserve_items_in_order()
                if instance.shipping_needed():
                    instance.status = 'wait_t_confirm'
                    OrderStatusTimestamp.stamp(instance, 'item_prepare')#####to cahgb wait_t_confirm
                    ##crest t req
                    src_branch = instance.items.first().currently_at
                    dst_branch = instance.user.branch
                    to_create_t_reqs = []
                    for order_item in instance.order_item_order.all():
                        new_t_req = TransferRequest(src_branch=src_branch, dst_branch=dst_branch,
                                                    req_sender=instance.user,
                                                    item=order_item.item, amount=order_item.amount, ref_order=instance)
                        to_create_t_reqs.append(new_t_req)
                        ItemLog.generate_log(new_t_req, instance.user, 'request_sent', related_order=instance)
                    TransferRequest.objects.bulk_create(to_create_t_reqs)


                else:
                    instance.status = 'item_ready'
                    instance.send_mail('item_ready')
                    OrderStatusTimestamp.stamp(instance, 'item_prepare')
                    OrderStatusTimestamp.stamp(instance, 'item_ready')



            elif (pre_save_status == 'item_prepare' or pre_save_status == 'item_ready' or pre_save_status == 'wait_t_confirm') and is_saving_status == 'canceled':
                OrderStatusTimestamp.stamp(instance, 'canceled')

            elif pre_save_status == 'item_ready' and is_saving_status == 'item_received':
                instance.make_items_unavailable()
                if not instance.due_date:
                    instance.due_date = timezone.now() + timezone.timedelta(days=7)
                OrderStatusTimestamp.stamp(instance, 'item_received')

            elif pre_save_status == 'item_received' and is_saving_status == 'item_returned':
                OrderStatusTimestamp.stamp(instance, 'item_returned')

            elif is_saving_status == 'done':
                instance.send_mail('done')
                OrderStatusTimestamp.stamp(instance, 'done')


pre_save.connect(change_order_status, sender=Order)

TRANSFER_REQUEST_STATUS_CHOICES = (

    ('request_sent', 'request_sent'),
    ('request_accepted', 'request_accepted'),
    ('dispatched', 'DISPATCHED'),
    ('received', 'RECEIVED'),
    ('canceled', 'CANCELED'),
)


class TransferRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    src_branch = models.ForeignKey(Branch, blank=True, on_delete=models.CASCADE,
                                   related_name='transfer_request_src_branch')
    dst_branch = models.ForeignKey(Branch, on_delete=models.CASCADE,
                                   related_name='transfer_request_dst_branch')
    req_sender = models.ForeignKey(USER, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='transfer_request_req_sender')
    req_receiver = models.ForeignKey(USER, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='transfer_request_req_receiver')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transfer_request_item')
    amount = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    status = models.CharField(max_length=20, default='request_sent', choices=TRANSFER_REQUEST_STATUS_CHOICES)
    ref_order = models.ForeignKey(Order, blank=True, null=True, on_delete=models.CASCADE,
                                  related_name='transfer_request')

    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-timestamp', 'ref_order')

    def has_valid_item_status(self):
        return self.item.status == 'available'

    def has_valid_item_amount(self):
        quantity = self.item.get_q_this_branch().get('available')
        if self.amount > quantity:
            return False
        return True

    def reserve_for_transfering(self):
        if self.has_valid_item_amount():
            if self.item.item_abstract.track_1by1:
                self.item.status = 'requested_to_be_transfered'
                self.item.save()
            else:
                shipping_obj = Item.objects.filter(item_abstract=self.item.item_abstract,
                                                   currently_at=self.item.currently_at,
                                                   status='shipping').first()

                shipping_obj.quantity += self.amount
                shipping_obj.save()

                if self.ref_order is not None:

                    reserved_obj = Item.objects.filter(item_abstract=self.item.item_abstract,
                                                       currently_at=self.item.currently_at,
                                                       status='reserved').first()

                    reserved_obj.quantity -= self.amount
                    reserved_obj.save()
                else:

                    self.item.quantity -= self.amount
                    self.item.save()

    def restore_item(self):
        if self.item.item_abstract.track_1by1 and not self.ref_order:
            self.item.status = 'available'
            self.item.save()
        elif self.item.item_abstract.track_1by1 and self.ref_order:
            for order_item in self.ref_order.order_item_order.all():

                order_item.item.status = 'available'
                order_item.item.save()

        elif not self.item.item_abstract.track_1by1 and not self.ref_order:
            shipping_obj = Item.objects.filter(item_abstract=self.item.item_abstract,
                                               currently_at=self.item.currently_at,
                                               status='shipping').first()
            shipping_obj.quantity -= self.amount
            shipping_obj.save()

            self.item.quantity += self.amount
            self.item.save()
        elif not self.item.item_abstract.track_1by1 and self.ref_order:
            reserved_item = Item.objects.filter(item_abstract=self.item.item_abstract,
                                               currently_at=self.item.currently_at,
                                               status='reserved').first()
            reserved_item.quantity -= self.amount
            reserved_item.save()

            self.item.quantity += self.amount
            self.item.save()



    def to_ship(self):
        if self.item.item_abstract.track_1by1:
            self.item.status = 'preparing_for_shipment'
            self.item.save()
        else:
            if self.ref_order:
                reserved_obj = Item.objects.filter(item_abstract=self.item.item_abstract,
                                                   currently_at=self.item.currently_at,
                                                   status='reserved').first()

                reserved_obj.quantity -= self.amount
                reserved_obj.save()

                shipping_obj = Item.objects.filter(item_abstract=self.item.item_abstract,
                                                   currently_at=self.item.currently_at,
                                                   status='shipping').first()
                shipping_obj.quantity += self.amount
                shipping_obj.save()

    def to_dispatch(self):
        if self.item.item_abstract.track_1by1:
            self.item.status = 'shipping'
            self.item.save()

    def receive_(self):

        if not Item.is_registered(self.item.item_abstract, self.dst_branch):
            new_item = Item.register(self.item.item_abstract, self.dst_branch)

        if self.item.item_abstract.track_1by1:
            if self.ref_order:
                self.item.status = 'reserved'
            else:
                self.item.status = 'available'
            self.item.currently_at = self.dst_branch
            self.item.save()
        else:
            shipping_obj = Item.objects.filter(item_abstract=self.item.item_abstract,
                                               currently_at=self.item.currently_at,
                                               status='shipping').first()
            shipping_obj.quantity -= self.amount
            shipping_obj.save()



            if self.ref_order:
                reserved_item = Item.objects.filter(
                    item_abstract=self.item.item_abstract,
                    currently_at=self.dst_branch,
                    status='reserved'
                ).first()
                reserved_item.quantity += self.amount
                reserved_item.save()
            else:
                dst_item = Item.objects.filter(
                    Q(item_abstract__serial=self.item.item_abstract.serial, currently_at=self.dst_branch,
                      status='available', tracking_number=self.item.tracking_number) |
                    Q(item_abstract__serial=self.item.item_abstract.serial, currently_at=self.dst_branch,
                      status='unavailable', tracking_number=self.item.tracking_number)
                ).distinct().first()

                dst_item.quantity += self.amount
                dst_item.save()




    #######################.filter(item_abstract__track_1by1=True)
    def all_items_in_ref_order_are_received(self):
        ref_order = self.ref_order
        items_in_ref_order = ref_order.items.all()

        test_get_shipping = items_in_ref_order.filter(item_abstract__track_1by1=True).filter(status='shipping')
        if test_get_shipping.count() > 0:
            return False
        return True

    def receive_with_ref_order(self):

        ref_order = self.ref_order
        if ref_order.status == 'item_prepare':
            self.receive_()

            if self.all_items_in_ref_order_are_received():
                ref_order.status = 'item_ready'
                ref_order.save()
                ref_order.send_mail('item_ready')
                OrderStatusTimestamp.stamp(ref_order, 'item_ready')


def change_transfer_request_status(sender, instance, *args, **kwargs):
    test_get_t_req = TransferRequest.objects.filter(id=instance.id)

    if test_get_t_req.count() > 0:
        pre_save_status = TransferRequest.objects.get(id=instance.id).status

        is_saving_status = instance.status

        if pre_save_status != is_saving_status:

            if pre_save_status == 'request_sent' and is_saving_status == 'canceled':

                instance.restore_item()

            elif pre_save_status == 'request_sent' and is_saving_status == 'request_accepted':
                instance.to_ship()

            elif pre_save_status == 'request_accepted' and is_saving_status == 'dispatched':

                instance.to_dispatch()
                # to shipping
            elif pre_save_status == 'dispatched' and is_saving_status == 'received':

                if instance.ref_order:
                    instance.receive_with_ref_order()
                else:
                    instance.receive_()

                # to available
                # if has order then change order status to item_ready

    else:
        if instance.status == 'request_sent':

            instance.reserve_for_transfering()


pre_save.connect(change_transfer_request_status, sender=TransferRequest)


