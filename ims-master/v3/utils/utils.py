from django.utils.text import slugify
import os, random

from django.conf import settings
import os.path


NAME_REGEX = '^\p{L}+$'

def unique_slug_generator(instance, new_slug=None):
    Klass = instance.__class__
    classname = instance.__class__.__name__

    if new_slug is not None:
        slug = new_slug
    elif classname == 'ItemAbstract':
        slug = slugify(instance.serial)
    else:
        slug = slugify(instance.alias)

    return slug


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)

    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):

    random_num = random.randint(6, 6666)
    classname = instance.__class__.__name__
    name, ext = get_filename_ext(filename)
    if classname == 'User':
        new_filename = f"{instance.username}_{random_num}"
        final_path = f"img/users/{new_filename}{ext}"
    elif classname == 'Branch':
        new_filename = f"{instance.title}_{random_num}"
        final_path = f"img/branches/{new_filename}{ext}"
    elif classname == 'ItemAbstract':
        new_filename = f"{instance.title}_{random_num}"
        final_path = f"img/itemabstracts/{new_filename}{ext}"

    else:
        new_filename = f"{instance.title}_{random_num}"
        final_path = f"img/nonono/{new_filename}{ext}"

    return final_path


def auto_tracking_number(instance, serial):
    Klass = instance.__class__
    last_tracking_number_obj = Klass.objects.filter(item_abstract__serial=serial).order_by('tracking_number').last()
    if not last_tracking_number_obj:
        return 0

    if last_tracking_number_obj.item_abstract.track_1by1:
        new_tracking_number = last_tracking_number_obj.tracking_number + 1
    else:
        new_tracking_number = last_tracking_number_obj.tracking_number
    return new_tracking_number


def increase_q(instance, increase_by):
    Klass = instance.__class__
    if instance.track_1by1:
        items = []
        for i in range(increase_by):
            new_item = Klass(item_abstract=instance.item_abstract, property_of=instance.property_of, track_1by1=True)
            items.append(new_item)
        Klass.objects.bulk_create(items)
    else:
        instance.quantity += increase_by
        instance.save()


def decrease_q(instance, decrease_by):
    Klass = instance.__class__
    if instance.track_1by1:

        items = Klass.objects.filter(item_serial=instance.item_serial, status='available')
        items.delete()
    else:
        instance.quantity -= decrease_by
        instance.save()
