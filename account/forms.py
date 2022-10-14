from datetime import timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.conf import settings
from .models import UrlUser, Activation

class UserCacheMixin:
    user_cache = None

class signupForm(UserCreationForm):
    email = forms.EmailField(max_length=224, help_text='A valid email address required')
    
    class Meta:
        model = UrlUser                 
        fields = ('email', 'username', 'firstname', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = UrlUser.objects.exclude(pk=self.instance.pk).get(email=email)
        except UrlUser.DoesNotExist:
            return email
        raise  forms.ValidationError("Email '%s' is already in use!" % email)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = UrlUser.objects.exclude(pk=self.instance.pk).get(username=username)
        except UrlUser.DoesNotExist:
            return username
        raise forms.ValidationError("Username '%s' is already is use!" % username)

class signinForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    class Meta:
        model = UrlUser
        fields = ('email', 'password',)
    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Invalid login credentials')
       
class EmailForm(UserCacheMixin, forms.Form):
    email = forms.EmailField(label='Email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = UrlUser.objects.get(email=email)
        except UrlUser.DoesNotExist:
            raise forms.ValidationError('You entered an invalid email address.')
        else:
            if not user.is_active:
                raise forms.ValidationError('This account is not active.')
        self.user_cache = user
        return email

class ResendActivationCodeForm(UserCacheMixin, forms.Form):
    email = forms.EmailField(label='Email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = UrlUser.objects.get(email=email)
        except UrlUser.DoesNotExist:
            raise forms.ValidationError('You entered an invalid email address.')
        else:
            
            if user.is_active:
                raise forms.ValidationError('This account has already been activated.')
            try:
                activation = Activation.objects.get(user=user)
            except Activation.DoesNotExist:
                raise forms.ValidationError('Activation code is not created for this account')
            else:
                currentTime = timezone.now() - timedelta(hours=24)
                if activation.createdAt > currentTime:
                    raise forms.ValidationError('Activation code has already been sent. You can request a new code in 24 hours')
                self.user_cache = user
                return email
    

class RemindUsernameForm(EmailForm):
    pass

class RestorePasswordForm(EmailForm):
    pass

class ProfileUpdateForm(UserCacheMixin,forms.ModelForm):
    class Meta:
        model = UrlUser
        fields = ('email', 'username', 'profile_image')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = UrlUser.objects.exclude(pk=self.instance.pk).get(email=email)
        except UrlUser.DoesNotExist:
            return email
        raise  forms.ValidationError("Email '%s' is already in use!" % email)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = UrlUser.objects.exclude(pk=self.instance.pk).get(username=username)
        except UrlUser.DoesNotExist:
            return username
        raise forms.ValidationError("Username '%s' is already is use!" % username)

    def save(self, commit=True):
        user = super(ProfileUpdateForm, self).save(commit=False)
        user.email         = self.cleaned_data['email']
        user.username      = self.cleaned_data['username']
        if commit:
            user.save() 
        return user