from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as USERMANAGER
from stdimage import StdImageField
from branches.models import Branch
from utils.utils import upload_image_path
from django.urls import reverse_lazy


class UserManager(USERMANAGER):

    def create_superuser(self, username, email, password, **extra_fields):

        user = self.create_user(
            username,
            email=self.normalize_email(email),
            password=password,
            user_type='administrator',
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True

        if Branch.objects.all().count() == 0:
            admin_branch = Branch.objects.create(title='ADMIN_', alias='admin', slug='admin')
            user.branch = admin_branch

        user.save(using=self._db)
        return user




class User(AbstractUser):
    user_type = models.CharField(max_length=15, default='normal' )
    image = StdImageField(upload_to=upload_image_path, blank=True, null=True,
                          delete_orphans=True,
                          )
    etc = models.CharField(max_length=150, blank=True)
    branch = models.ForeignKey(Branch, blank=True, null=True, on_delete=models.SET_NULL, related_name='users')

    objects = UserManager()

    class Meta:
        ordering = [
            'user_type', 'username'
        ]
    def get_absolute_url(self):

        return reverse_lazy("branches:user_detail", kwargs={"branch_slug": self.branch.slug, "username": self.username})

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True