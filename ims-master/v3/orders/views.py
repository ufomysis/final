from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
from .models import Order, OrderStatusTimestamp, Item
from .forms import SelectDueDateForm, EditNoteForm
from .filter import OrderFilter
from django.contrib.auth import get_user_model
from utils.decorators import inv_manager_ad_required_fbv, inv_manager_owner_required_fbv
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
USER = get_user_model()


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/list_view/list.html"

    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        context['filter'] = OrderFilter(self.request.GET)
        context['branch'] = self.request.user.branch

        return context

    def get_queryset(self):
        branch = self.request.user.branch

        if self.request.user.user_type == 'inv_manager':

            qs = self.model.objects.filter(user__branch=branch).distinct()
        elif self.request.user.user_type == 'administrator':
            qs = self.model.objects.all()
        else:
            qs = self.model.objects.filter(user=self.request.user).distinct()

        filtered_list = OrderFilter(self.request.GET, queryset=qs)
        return filtered_list.qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/detail_view/main.html"

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['SelectDueDateForm'] = SelectDueDateForm()
        context['EditNoteForm'] = EditNoteForm()
        context['StatusTimestamp'] = OrderStatusTimestamp.get_status_timestamps(self.object)

        return context


@inv_manager_owner_required_fbv
def order_cancel(request, order_id):
    if request.method == "POST":

        order_obj = Order.objects.get(id=order_id)

        pre_save_status = order_obj.status
        if pre_save_status == 'item_prepare' or pre_save_status == 'item_ready' or pre_save_status == 'wait_t_confirm':

            if order_obj.transfer_request:
                for t_req in order_obj.transfer_request.all():
                    t_req.status = 'canceled'
                    t_req.save()

            order_obj.status = 'canceled'
            order_obj.save()

            Order.restore_items(order_obj, current_branch=request.user.branch)
            order_obj.send_mail('canceled', request_user=request.user)

        return redirect('orders:detail', pk=order_id)


@inv_manager_ad_required_fbv
def order_give_items(request, order_id):
    if request.method == "POST":
        due_date_form = SelectDueDateForm(request.POST)
        order_obj = Order.objects.get(id=order_id)

        pre_save_status = order_obj.status
        if pre_save_status == 'item_ready':
            order_obj.inv_manager = request.user

            test_get_item = order_obj.items.filter(item_abstract__track_1by1=False)
            if test_get_item.count() > 0:
                order_obj.status = 'done'
                order_obj.save()

                reserved = Item.objects.filter(currently_at=request.user.branch, status='reserved',
                                               item_abstract__serial=test_get_item.first().item_abstract.serial).first()
                reserved.quantity -= order_obj.order_item_order.first().amount
                reserved.save()
            else:
                order_obj.status = 'item_received'
                if due_date_form.is_valid():
                    order_obj.due_date = due_date_form.cleaned_data.get('due_date')
                    order_obj.save()
                else:
                    messages.error(request, 'ตรวจสอบวันที่ใหม่')


        return redirect('orders:detail', pk=order_id)


@inv_manager_ad_required_fbv
def order_take_back(request, order_id):
    if request.method == "POST":

        order_obj = Order.objects.get(id=order_id)
        pre_save_status = order_obj.status
        if pre_save_status == 'item_received':

            if timezone.localtime() > order_obj.due_date:
                order_obj.status = 'overdue'
            else:
                order_obj.status = 'item_returned'
                Order.restore_items(order_obj, current_branch=request.user.branch)

            order_obj.save()

        return redirect('orders:detail', pk=order_id)


@inv_manager_ad_required_fbv
def order_mark_done(request, order_id):
    if request.method == "POST":
        order_obj = Order.objects.get(id=order_id)

        order_obj.status = 'done'
        order_obj.save()

        return redirect('orders:detail', pk=order_id)


@inv_manager_ad_required_fbv
def edit_note(request, order_id):
    if request.method == "POST":
        order_obj = Order.objects.get(id=order_id)
        edit_note_form = EditNoteForm(request.POST)
        if edit_note_form.is_valid():
            order_obj.note = edit_note_form.cleaned_data.get('note')
            order_obj.save()

        return redirect('orders:detail', pk=order_id)


@login_required
def get_order_report(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    template_name = 'orders/receipt.html'
    context = {
        "object": order,

    }

    return render(request, template_name, context)
