from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .manager import MyAccountManager

def get_profile_image_filepath(self, filename):
    return f'profile_image/{self.pk}/{"profile_image.png"}'

def get_default_profile_image():
    return 'default/user_logo.jpg'

class UrlUser(AbstractBaseUser):
    email          = models.EmailField(verbose_name='email', max_length=60, unique=True)
    firstname       = models.CharField(max_length=15)
    username       = models.CharField(max_length=30, unique=True)
    date_joined    = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login     = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin       = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    is_superuser   = models.BooleanField(default=False)
    profile_image  = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)

    objects = MyAccountManager()


    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD     = 'email'
    
    def __str__(self):
        return self.username
    
    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index(f'profile_image/{self.pk}/'):]
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

class Activation(models.Model):
    user      = models.ForeignKey(UrlUser, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    code      = models.CharField(max_length=20, unique=True)
    email     = models.EmailField()

class Urls(models.Model):
    user      = models.ForeignKey(UrlUser, on_delete=models.CASCADE)
    old_url   = models.TextField()
    new_url   = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
     

