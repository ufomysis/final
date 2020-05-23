from django.shortcuts import render, redirect, HttpResponseRedirect, get_list_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.db import transaction

from items.models import Item, Branch, ItemLog
from orders.models import Order, Order_Item
from .forms import BorrowForm
from .filter import CatalogListFilter, CatalogDetailFilter


from django.contrib.auth import get_user_model

USER = get_user_model()


class CatalogListView(ListView):
    model = Item
    template_name = "orders/catalog/list/list.html"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(CatalogListView, self).get_context_data(**kwargs)
        context['filter'] = CatalogListFilter(self.request.GET)
        context['borrow_form'] = BorrowForm()

        return context

    def get_queryset(self):
        qs = self.model.objects.get_all_list_ver()
        filtered_list = CatalogListFilter(self.request.GET, queryset=qs)

        return filtered_list.qs


class CatalogDetailView(ListView):
    model = Item
    template_name = "orders/catalog/detail/detail.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(CatalogDetailView, self).get_context_data(**kwargs)
        context['info_id'] = self.kwargs.get('info_id')
        info_obj = self.model.get_info_obj_by_id(context['info_id'])
        context['info'] = info_obj
        context['borrow_form'] = BorrowForm()
        context['filter'] = CatalogDetailFilter(self.request.GET)


        return context

    def get_queryset(self):
        info_id = self.kwargs.get('info_id')
        qs = Item.get_qs_by_info_id(info_id)
        filtered_list = CatalogDetailFilter(self.request.GET, queryset=qs)

        return filtered_list.qs


@transaction.atomic
def borrow(request, info_id):
    if request.method == 'POST':
        item_id = request.POST['item_id']
        info_obj = Item.get_info_obj_by_id(info_id)
        test_item_obj = Item.objects.get(id=item_id)
        if not test_item_obj.item_abstract.track_1by1:
            amount = int(request.POST['amount'])
        else:
            amount = 1

        if amount > test_item_obj.quantity:
            messages.error(request, 'ไม่อนุญาตให้ยืมมากกว่าจำนวนอุปกรณ์ที่มี')
        elif amount < 1:
            messages.error(request, 'ไม่อนุญาตให้ระบุจำนวนน้อยกว่า 1')
        elif test_item_obj.status != 'available':
            messages.error(request,
                           f"อุปกรณ์ชื่อ: {test_item_obj.item_abstract.title} รหัส: {test_item_obj.item_abstract.serial} หมายเลขติดตาม: {test_item_obj.tracking_number} ไม่ได้อยู่ในสถานะว่างแล้ว")

        else:
            new_order = Order.objects.create(user=request.user)
            Order_Item.objects.create(item=test_item_obj, order=new_order, amount=amount)

            new_order.status = 'created'
            new_order.save()
            messages.success(request, 'สร้างรายการเบิกใช้อุปกรณ์เรียบร้อยแล้ว')

    return redirect('catalog:detail', info_id=info_id)


@transaction.atomic
def borrow_multiple(request):
    if request.method == 'POST':

        info_id = request.POST['info_id']

        info_obj = Item.get_info_obj_by_id(info_id)

        amount = int(request.POST['amount'])
        available_q = info_obj.get_q_this_branch().get('available')

        if amount > available_q:
            messages.error(request, 'ไม่อนุญาตให้ยืมมากกว่าจำนวนอุปกรณ์ที่มี')
        elif amount < 1:
            messages.error(request, 'ไม่อนุญาตให้ระบุจำนวนน้อยกว่า 1')

        else:
            new_order = Order.objects.create(user=request.user)

            if info_obj.item_abstract.track_1by1:
                selected_ids = Item.objects.filter(item_abstract=info_obj.item_abstract,
                                                   currently_at=info_obj.currently_at, status='available').order_by(
                    '-tracking_number')[:amount].values_list("id", flat=True)
                selected_items_obj = Item.objects.filter(id__in=list(selected_ids)).all()

                to_create_order_items = []
                for item in selected_items_obj:
                    new_order_item = Order_Item(item=item, order=new_order)
                    to_create_order_items.append(new_order_item)
                Order_Item.objects.bulk_create(to_create_order_items)

            else:
                track1_item = Item.objects.get(item_abstract=info_obj.item_abstract, currently_at=info_obj.currently_at,
                                               status='available')
                Order_Item.objects.create(item=track1_item, order=new_order, amount=amount)

            new_order.status = 'created'
            new_order.save()
            messages.success(request, 'สร้างรายการเบิกใช้อุปกรณ์เรียบร้อยแล้ว')

        return redirect('catalog:list')
