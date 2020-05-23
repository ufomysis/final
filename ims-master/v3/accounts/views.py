from django.shortcuts import render, redirect, get_object_or_404

from .forms import UserCreateUpdateModelForm, ProfileUpdate

from branches.models import Branch
from django.forms import modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .filter import UserFilter

USER = get_user_model()
from utils.decorators import ad_required_fbv, profile_owner_only


class UserListView(ListView):
    model = USER
    template_name = "accounts/list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['filter'] = UserFilter(self.request.GET)
        branch_slug = self.kwargs.get('branch_slug')
        if branch_slug.lower() == 'all':
            context['branch_title'] = 'ทั้งหมด'
            context['branch_slug'] = 'all'
        else:
            context['branch_title'] = Branch.objects.get(slug=branch_slug).title
            context['branch_slug'] = Branch.objects.get(slug=branch_slug).slug

        return context

    def get_queryset(self):
        branch_slug = self.kwargs.get('branch_slug')
        if branch_slug.lower() == 'all':
            qs = self.model.objects.all()
        else:
            qs = self.model.objects.filter(branch__slug=branch_slug)
        filtered_list = UserFilter(self.request.GET, queryset=qs)
        return filtered_list.qs


def user_detail_view(request, branch_slug, username):
    if branch_slug == 'all':
        obj = get_object_or_404(USER, username=username)
    else:
        obj = get_object_or_404(USER, branch__slug=branch_slug, username=username)
    template_name = 'accounts/detail.html'
    context = {
        "object": obj,
        'branch_slug': branch_slug,

    }

    if obj.branch:
        context['branch_title'] = obj.branch.title
    else:
        context['branch_title'] = 'ทั้งหมด'

    return render(request, template_name, context)


@ad_required_fbv
def user_update_admin_view(request, branch_slug, username):
    if branch_slug == 'all':
        obj = get_object_or_404(USER, username=username)
    else:
        obj = get_object_or_404(USER, branch__slug=branch_slug, username=username)
    form = UserCreateUpdateModelForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('branches:user_list', branch_slug=branch_slug)

    template_name = 'accounts/update.html'
    context = {
        "object": obj,
        'form': form,
        'branch_slug': branch_slug,
    }
    if obj.branch:
        context['branch_title'] = obj.branch.title
    else:
        context['branch_title'] = 'ทั้งหมด'

    return render(request, template_name, context)


@ad_required_fbv
def user_delete_view(request, branch_slug, username):
    if request.method == "POST":
        obj = get_object_or_404(USER, username=username)
        obj.delete()
    return redirect('branches:user_list', branch_slug=branch_slug)


@ad_required_fbv
def user_bulk_create_view_admin(request, branch_slug):
    branch = Branch.objects.get(slug=branch_slug)

    UserFormSet = modelformset_factory(model=USER, form=UserCreateUpdateModelForm)

    formset = UserFormSet(request.POST or None, request.FILES or None, queryset=USER.objects.none())

    if formset.is_valid():

        instances = formset.save(commit=False)

        for instance in instances:
            instance.branch = branch
            instance.save()

        return redirect('branches:user_list', branch_slug=branch_slug)



    context = {
        'formset': formset,
        'branch_slug': branch_slug,
    }

    if branch:
        context['branch_title'] = branch.title
    else:
        context['branch_title'] = 'ทั้งหมด'


    return render(request, 'accounts/create_bulk.html', context)


@login_required
def user_profile_detail_view(request):
    obj = get_object_or_404(USER, username=request.user.username)
    template_name = 'accounts/profile/home.html'
    context = {"object": obj}
    return render(request, template_name, context)


@login_required
def user_profile_update(request):
    form = ProfileUpdate(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('profile:home')
    template_name = 'accounts/profile/update.html'
    context = {
        'form': form,
    }
    return render(request, template_name, context)
