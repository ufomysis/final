from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy

from .models import Branch
from .filter import BranchFilter
from .forms import BranchCreateUpdateModelForm
from utils.utils import unique_slug_generator

from django.contrib.auth import get_user_model
from utils.decorators import ad_required_cbv, ad_required_fbv

USER = get_user_model()


class BranchListView(ListView):
    model = Branch
    template_name = "branches/list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(BranchListView, self).get_context_data(**kwargs)
        context['filter'] = BranchFilter(self.request.GET)

        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_list = BranchFilter(self.request.GET, queryset=qs)
        return filtered_list.qs


class BranchDetailView(DetailView):
    model = Branch
    template_name = "branches/detail.html"
    slug_url_kwarg = "branch_slug"


class BranchCreateView(CreateView):
    form_class = BranchCreateUpdateModelForm
    template_name = "branches/create.html"
    success_url = reverse_lazy('branches:branch_list')

    @ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(BranchCreateView, self).dispatch(*args, **kwargs)


class BranchUpdateView(UpdateView):
    model = Branch
    form_class = BranchCreateUpdateModelForm
    template_name = "branches/update.html"
    slug_url_kwarg = "branch_slug"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.slug = unique_slug_generator(obj)
        obj.save()
        return super(BranchUpdateView, self).form_valid(form)

    @ad_required_cbv
    def dispatch(self, *args, **kwargs):
        return super(BranchUpdateView, self).dispatch(*args, **kwargs)


@ad_required_fbv
def branch_delete_view(request, branch_slug):
    if request.method == "POST":
        obj = get_object_or_404(Branch, slug=branch_slug)
        obj.delete()
    return redirect('branches:branch_list')
