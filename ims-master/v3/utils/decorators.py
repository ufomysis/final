from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from itemabstracts.models import ItemAbstract
from orders.models import Order
USER = get_user_model()


def profile_owner_only(function):
    def wrap(request, username, *args, **kwargs):
        owner = get_object_or_404(USER, username=username)

        if request.user.is_authenticated and request.user.username == owner:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def itemabstracts_edit_perm_cbv(function):
    def wrap(view, *args, **kwargs):
        current_user = view.request.user
        author = view.get_object().added_by
        allow_non_author_edit = view.get_object().allow_non_author_edit

        if current_user.is_authenticated:
            if allow_non_author_edit:
                if current_user.user_type == 'inv_manager' or current_user.user_type == 'administrator':
                    return function(view, *args, **kwargs)
            else:
                if current_user == author or current_user.user_type == 'administrator':
                    return function(view, *args, **kwargs)

        raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def itemabstracts_edit_perm_fbv(function):
    def wrap(request, slug, *args, **kwargs):
        current_user = request.user
        instance = ItemAbstract.objects.filter(slug=slug).first()
        author = instance.added_by
        allow_non_author_edit = instance.allow_non_author_edit

        if current_user.is_authenticated:
            if allow_non_author_edit:
                if current_user.user_type == 'inv_manager' or current_user.user_type == 'administrator':
                    return function(request, slug, *args, **kwargs)
            else:
                if current_user == author or current_user.user_type == 'administrator':
                    return function(request, slug, *args, **kwargs)

        raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def inv_manager_ad_required_fbv(function):
    def wrap(request, *args, **kwargs):

        if request.user.is_authenticated and (
                request.user.user_type == 'inv_manager' or request.user.user_type == 'administrator'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def auditor_ad_required_fbv(function):
    def wrap(request, *args, **kwargs):

        if request.user.is_authenticated and (
                request.user.user_type == 'auditor' or request.user.user_type == 'administrator'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def inv_manager_ad_required_cbv(function):
    def wrap(view, *args, **kwargs):
        current_user = view.request.user

        if current_user.is_authenticated and (
                current_user.user_type == 'inv_manager' or current_user.user_type == 'administrator'):
            return function(view, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def auditor_ad_required_cbv(function):
    def wrap(view, *args, **kwargs):
        current_user = view.request.user

        if current_user.is_authenticated and (
                current_user.user_type == 'auditor' or current_user.user_type == 'administrator'):
            return function(view, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def ad_required_cbv(function):
    def wrap(view, *args, **kwargs):
        current_user = view.request.user

        if current_user.is_authenticated and current_user.user_type == 'administrator':
            return function(view, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def ad_required_fbv(function):
    def wrap(request, *args, **kwargs):

        if request.user.is_authenticated and request.user.user_type == 'administrator':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def inv_manager_owner_required_fbv(function):
    def wrap(request, order_id, *args, **kwargs):

        current_user = request.user
        order_instance = get_object_or_404(Order, id=order_id)
        owner = order_instance.user

        if request.user.is_authenticated and (
                request.user.user_type == 'inv_manager' or request.user.user_type == 'administrator') or request.user.is_authenticated and current_user == owner:
            return function(request, order_id, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap