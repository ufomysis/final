from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Unit, Category
from items.models import Item, ItemAbstract, ItemLog
from .filter import UnitFilter, CategoryFilter, ItemAbstractFilter
from .forms import UnitCreateUpdateModelForm, CategoryCreateUpdateModelForm, ItemAbstractCreateForm, \
    ItemAbstractUpdateForm
from utils.utils import unique_slug_generator
from utils.decorators import itemabstracts_edit_perm_fbv, itemabstracts_edit_perm_cbv, inv_manager_ad_required_fbv, \
    inv_manager_ad_required_cbv

from django.contrib.auth import get_user_model

USER = get_user_model()


class UnitListView(ListView):
    model = Unit
    template_name = "itemabstracts/units/list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(UnitListView, self).get_context_data(**kwargs)
        context['filter'] = UnitFilter(self.request.GET)
        context['create_form'] = UnitCreateUpdateModelForm(self.request.POST or None)

        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = UnitFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(UnitListView, self).dispatch(*args, **kwargs)


@inv_manager_ad_required_fbv
def unit_create_view(request):
    if request.method == 'POST':
        form = UnitCreateUpdateModelForm(request.POST)
        if form.is_valid():
            new_obj = form.save(commit=False)
            new_obj.added_by = request.user
            new_obj.updated_by = request.user
            new_obj.save()
        else:
            messages.warning(request, 'โปรดตรวจสอบความถูกต้องของชื่อหน่วยนับ')
        return redirect('units:list')


@inv_manager_ad_required_fbv
def unit_delete_view(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(Unit, pk=pk)
        if obj.item_abstract_unit.all().count() > 0 :
            messages.error(request, "ข้อมูลหน่วยนับนี้มีการใช้งานอยู่")
        else:
            obj.delete()
    return redirect('units:list')


class CategoryListView(ListView):
    model = Category
    template_name = "itemabstracts/categories/list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['filter'] = UnitFilter(self.request.GET)
        context['create_form'] = CategoryCreateUpdateModelForm(self.request.POST or None)

        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = CategoryFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(CategoryListView, self).dispatch(*args, **kwargs)


@inv_manager_ad_required_fbv
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryCreateUpdateModelForm(request.POST)
        if form.is_valid():
            new_obj = form.save(commit=False)
            new_obj.added_by = request.user
            new_obj.updated_by = request.user
            new_obj.save()
        else:
            messages.warning(request, 'โปรดตรวจสอบความถูกต้องของชื่อประเภท')
        return redirect('categories:list')


@inv_manager_ad_required_fbv
def category_delete_view(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(Category, pk=pk)
        if obj.item_abstract_category.all().count() > 0 :
            messages.error(request, "ข้อมูลหประเภทนี้มีการใช้งานอยู่")
        else:
            obj.delete()
    return redirect('categories:list')


class ItemAbstractListView(ListView):
    model = ItemAbstract
    template_name = "itemabstracts/list.html"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ItemAbstractListView, self).get_context_data(**kwargs)
        context['filter'] = ItemAbstractFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = ItemAbstractFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(ItemAbstractListView, self).dispatch(*args, **kwargs)


class ItemAbstractCreateView(CreateView):
    form_class = ItemAbstractCreateForm
    template_name = "itemabstracts/create.html"
    success_url = reverse_lazy('itemabstracts:list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.added_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return super(ItemAbstractCreateView, self).form_valid(form)

    @inv_manager_ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(ItemAbstractCreateView, self).dispatch(*args, **kwargs)


class ItemAbstractUpdateView(UpdateView):
    model = ItemAbstract
    form_class = ItemAbstractUpdateForm
    template_name = "itemabstracts/update.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.slug = unique_slug_generator(obj)
        obj.save()
        return super(ItemAbstractUpdateView, self).form_valid(form)

    @itemabstracts_edit_perm_cbv
    def dispatch(self, *args, **kwargs):
        return super(ItemAbstractUpdateView, self).dispatch(*args, **kwargs)


@itemabstracts_edit_perm_fbv
def item_abstracts_delete_view(request, slug):
    if request.method == "POST":
        obj = get_object_or_404(ItemAbstract, slug=slug)
        if obj.item.all().count() > 0 :
            messages.error(request, "ข้อมูลอุปกรณ์นี้มีการใช้งานอยู่")
        else:
            obj.delete()
    return redirect('itemabstracts:list')


@inv_manager_ad_required_fbv
def item_abstract_detail_view(request, slug):
    object = get_object_or_404(ItemAbstract, slug=slug)

    template_name = 'itemabstracts/detail.html'
    context = {
        "object": object,
        "is_registered": Item.is_registered(object, request.user.branch),

    }

    return render(request, template_name, context)


@inv_manager_ad_required_fbv
def add_item(request, slug):
    if request.method == "POST":

        item_abstract_obj = ItemAbstract.objects.get(slug=slug)
        currently_at_obj = request.user.branch

        is_registered = Item.is_registered(item_abstract_obj, currently_at_obj)

        if not is_registered:
            new_item = Item.register(item_abstract_obj, currently_at_obj)
            messages.success(request, "ลงทะเบียนอุปกรณ์สู่คลังสาขาสำเร็จ")
            ItemLog.generate_log(new_item, request.user, 'register_item')
        else:
            messages.error(request, 'อุปกรณ์นี้ลงทะเบียนไปแล้ว')
    else:
        messages.error(request, 'ลงทะเบียนไม่สำเร็จกรุณาตรวจสอบความถูกต้องและลงทะเบียนอีกครั้ง')

    return redirect('itemabstracts:detail', slug=slug)
