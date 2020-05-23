from django.shortcuts import render, redirect
from django.views.generic import ListView

from django.contrib import messages

from branches.views import BranchListView
from .models import Item, Branch, ItemLog
from orders.models import TransferRequest
from .filter import SerialFilter, LogFilter, T_Request_Filter

from .forms import EditItemQuantityForm, TransferForm

from django.contrib.auth import get_user_model
from utils.decorators import inv_manager_ad_required_fbv, inv_manager_ad_required_cbv

USER = get_user_model()


class InventoryListView(BranchListView):
    template_name = 'items/branch/list.html'

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(InventoryListView, self).dispatch(*args, **kwargs)


class SerialListView(ListView):
    model = Item
    template_name = "items/serial/list.html"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(SerialListView, self).get_context_data(**kwargs)
        context['filter'] = SerialFilter(self.request.GET)
        context['branch_slug'] = self.kwargs.get('branch_slug')
        context['branch_title'] = Branch.objects.get(slug=context['branch_slug']).title

        return context

    def get_queryset(self):
        branch_slug = self.kwargs.get('branch_slug')
        qs = self.model.objects.get_all_current_branch_only_list_ver(branch_slug)
        filtered_list = SerialFilter(self.request.GET, queryset=qs)

        return filtered_list.qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(SerialListView, self).dispatch(*args, **kwargs)


class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ItemListView, self).get_context_data(**kwargs)
        context['branch_slug'] = self.kwargs.get('branch_slug')
        context['branch_title'] = Branch.objects.get(slug=context['branch_slug']).title
        context['iabstract_slug'] = self.kwargs.get('iabstract_slug')
        info_obj = self.model.get_info_obj(context['iabstract_slug'], context['branch_slug'])
        context['info'] = info_obj
        context['quantity'] = {
            'all_branches': info_obj.get_q_all_branches(),
            'this_branch': info_obj.get_q_this_branch(),
        }

        context['is_empty_inv'] = info_obj.is_empty_inv()  ####
        context['edit_q_form'] = EditItemQuantityForm(self.request.POST or None, info_obj=info_obj)
        context['transfer_form'] = TransferForm(src_branch_slug=self.kwargs.get('branch_slug'))

        return context

    def get_queryset(self):
        branch_slug = self.kwargs.get('branch_slug')
        iabstract_slug = self.kwargs.get('iabstract_slug')
        qs = self.model.objects.get_by_iabstract_slug_currently_at_slug_detail_ver(iabstract_slug, branch_slug)

        return qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(ItemListView, self).dispatch(*args, **kwargs)


@inv_manager_ad_required_fbv
def edit_quantity(request, branch_slug, iabstract_slug):
    if request.method == 'POST':
        info_obj = Item.get_info_obj(iabstract_slug, branch_slug)
        form = EditItemQuantityForm(request.POST, info_obj=info_obj)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')
            if quantity > 0:
                info_obj.increase_quantity(quantity)
                ItemLog.generate_log(info_obj, request.user, 'increase_q', quantity)

            else:
                info_obj.decrease_quantity(quantity)
                ItemLog.generate_log(info_obj, request.user, 'decrease_q', quantity)

            messages.success(request, "แก้ไขจำนวนสำเร็จ")

        else:
            messages.error(request, 'กรุณาตรวจสอบความถูกต้องของจำนวน')

        return redirect('items:item_list', branch_slug=branch_slug, iabstract_slug=iabstract_slug)


@inv_manager_ad_required_fbv
def deregister(request, branch_slug, iabstract_slug):
    if request.method == 'POST':
        info_obj = Item.get_info_obj(iabstract_slug, branch_slug)

        if info_obj.is_empty_inv():
            del_info = info_obj.deregister()
            messages.success(request,
                             f"นำข้อมูลอุปกรณ์ ชื่อ: {del_info.item_abstract.title} รหัส: {del_info.item_abstract.serial} ออกจากคลังสาขาเรียบร้อยแล้ว")
            ItemLog.generate_log(del_info, request.user, 'deregister_item')
            return redirect('items:serial_list', branch_slug=branch_slug)
        else:
            messages.error(request, "การดำเนินการไม่สำเร็จ กรุณานำอุปกรณ์ออกจากคลังสาขาให้หมดก่อน")

        return redirect('items:item_list', branch_slug=branch_slug, iabstract_slug=iabstract_slug)


class TransferRequestListView(ListView):
    model = TransferRequest
    template_name = 'items/t_order/list.html'

    def get_context_data(self, **kwargs):
        context = super(TransferRequestListView, self).get_context_data(**kwargs)
        context['filter'] = T_Request_Filter(self.request.GET)

        return context

    def get_queryset(self):
        branch = self.request.user.branch
        if self.request.user.user_type == 'administrator':
            qs = self.model.objects.all()
        else:
            qs = self.model.objects.filter(src_branch=branch) | self.model.objects.filter(dst_branch=branch)
        filtered_list = T_Request_Filter(self.request.GET, queryset=qs)

        return filtered_list.qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(TransferRequestListView, self).dispatch(*args, **kwargs)


@inv_manager_ad_required_fbv
def send_transfer_request(request, branch_slug, iabstract_slug):
    if request.method == 'POST':
        item_id = request.POST['item_id']
        src_branch_slug = branch_slug

        test_item_obj = Item.objects.get(id=item_id)

        amount = int(request.POST['amount'])
        dst_branch_id = int(request.POST['dst_branch'])
        req_sender = request.user

        if amount > test_item_obj.quantity:
            messages.error(request, 'ไม่อนุญาตให้ยืมมากกว่าจำนวนอุปกรณ์ที่มี')
        elif amount < 1:
            messages.error(request, 'ไม่อนุญาตให้ระบุจำนวนน้อยกว่า 1')
        elif test_item_obj.status != 'available':
            messages.error(request,
                           f"อุปกรณ์ชื่อ: {test_item_obj.item_abstract.title} บาร์โค้ด: {test_item_obj.item_abstract.serial} หมายเลขติดตาม: {test_item_obj.tracking_number} ไม่ได้อยู่ในสถานะว่างแล้ว")


        else:
            src_branch = Branch.objects.get(slug=src_branch_slug)
            dst_branch = Branch.objects.get(id=dst_branch_id)

            t_req_object = TransferRequest.objects.create(src_branch=src_branch, dst_branch=dst_branch,
                                                          req_sender=req_sender, item=test_item_obj, amount=amount)

            ItemLog.generate_log(t_req_object, request.user, 'request_sent', related_order=None)

    return redirect('items:item_list', branch_slug=branch_slug, iabstract_slug=iabstract_slug)


@inv_manager_ad_required_fbv
def accept_transfer_request(request):
    if request.method == 'POST':
        req_id = request.POST['req_id']
        t_req_object = TransferRequest.objects.get(id=req_id)

        pre_save_status = t_req_object.status
        if pre_save_status == 'request_sent':
            t_req_object.status = 'request_accepted'
            t_req_object.req_receiver = request.user
            t_req_object.save()

            if t_req_object.ref_order:
                t_req_object.ref_order.status = 'item_prepare'
                t_req_object.ref_order.save()

                ref_order = t_req_object.ref_order
            else:
                ref_order = None
            ItemLog.generate_log(t_req_object, request.user, 'request_accepted', related_order=ref_order)

    return redirect('t_orders:list')


@inv_manager_ad_required_fbv
def cancel_transfer_request(request):
    if request.method == 'POST':
        req_id = request.POST['req_id']
        t_req_object = TransferRequest.objects.get(id=req_id)
        pre_save_status = t_req_object.status
        if pre_save_status == 'request_sent':
            if t_req_object.ref_order:
                ref_order = t_req_object.ref_order
                for t_req in ref_order.transfer_request.all():
                    t_req.status = 'canceled'
                    t_req.req_receiver = request.user
                    t_req.save()

                ref_order.status = 'canceled'
                ref_order.send_mail('canceled', request_user=request.user)
                ref_order.save()

            else:
                t_req_object.status = 'canceled'
                t_req_object.req_receiver = request.user
                t_req_object.save()
                ref_order = None

            ItemLog.generate_log(t_req_object, request.user, 'canceled', related_order=ref_order)

    return redirect('t_orders:list')


@inv_manager_ad_required_fbv
def dispatch(request):
    if request.method == 'POST':
        req_id = request.POST['req_id']
        t_req_object = TransferRequest.objects.get(id=req_id)
        pre_save_status = t_req_object.status
        if pre_save_status == 'request_accepted':

            t_req_object.status = 'dispatched'
            t_req_object.save()
            if t_req_object.ref_order:
                ref_order = t_req_object.ref_order
            else:
                ref_order = None

            ItemLog.generate_log(t_req_object, request.user, 'dispatched', related_order=ref_order)

    return redirect('t_orders:list')


@inv_manager_ad_required_fbv
def take_in(request):
    if request.method == 'POST':
        req_id = request.POST['req_id']
        t_req_object = TransferRequest.objects.get(id=req_id)

        pre_save_status = t_req_object.status
        if pre_save_status == 'dispatched':
            t_req_object.status = 'received'
            t_req_object.save()
            if t_req_object.ref_order:
                ref_order = t_req_object.ref_order
            else:
                ref_order = None
            ItemLog.generate_log(t_req_object, request.user, 'received', related_order=ref_order)

    return redirect('t_orders:list')


class ItemLogListView(ListView):
    model = ItemLog
    template_name = "items/log/list.html"

    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ItemLogListView, self).get_context_data(**kwargs)
        context['filter'] = LogFilter(self.request.GET)
        context['branch'] = self.kwargs.get('branch')

        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = LogFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(ItemLogListView, self).dispatch(*args, **kwargs)


@inv_manager_ad_required_fbv
def get_barcodes(request, iabstract_slug, branch_slug):
    items = Item.objects.get_by_iabstract_slug_currently_at_slug_detail_ver(iabstract_slug, branch_slug)
    branch = Branch.objects.get(slug=branch_slug)
    branch_name = branch.title

    template_name = 'items/barcode.html'
    context = {
        "object_list": items,
        "branch_name": branch_name,
        'serial': iabstract_slug,
        'branch_slug': branch_slug

    }

    return render(request, template_name, context)


@inv_manager_ad_required_fbv
def get_barcodes_all(request, iabstract_slug, branch_slug, get_all_b='one'):
    items = Item.objects.get_by_serial_no_info(iabstract_slug)
    branch_name = 'ทุกสาขา'

    template_name = 'items/barcode.html'
    context = {
        "object_list": items,
        "branch_name": branch_name,
        'serial': iabstract_slug,
        'branch_slug': branch_slug

    }

    return render(request, template_name, context)
