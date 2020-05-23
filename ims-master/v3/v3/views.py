from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import render
from accounts.forms import UserLoginForm
from django.contrib.auth.decorators import login_required

USER = get_user_model()


@login_required
def home_ri(request):
    if request.user.user_type == 'administrator':
        return redirect('branches:branch_list')
    elif request.user.user_type == 'inv_manager':
        return redirect('items:branch_list')
    elif request.user.user_type == 'auditor':
        return redirect('audit_session:list')

    return redirect('catalog:list')


def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user_obj = form.cleaned_data.get('user_obj')
        login(request, user_obj)
        return redirect('home')
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login_view')

