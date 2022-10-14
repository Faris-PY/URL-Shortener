from django.shortcuts import render, render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.views.generic import View

from django.core.files.storage import default_storage, FileSystemStorage
from django.core import files
import os
import json
import numpy
import cv2
import base64
import requests
from os.path import dirname

from django.conf import settings

from .models import Activation, UrlUser
from .utils import send_activation_email, send_userNameForgot_email, send_passwordReset_email
from .forms import ( signupForm, signinForm, RemindUsernameForm, RestorePasswordForm, ResendActivationCodeForm,
                     ProfileUpdateForm
                    )

TEMP_PROFILE_IMAGE_NAME = 'temp_profile_image.png'

class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

class SignupView(GuestOnlyView, View):

    def get(self, request):
        return render(request, 'account/signup.html')
    
    def post(self, request):
        context = {}
        form = signupForm(request.POST)
        if form.is_valid():
            user = form.save()
            os.mkdir(settings.MEDIA_ROOT + "/" + 'profile_image' + '/'+ str(user.pk))
            imageurl = user.profile_image
            user.profile_image.save("profile_image.png", imageurl)
            user.save()

            if settings.ENABLE_USER_ACTIVATION:
                user.is_active = False
                user.save()
                code = get_random_string(20)
                activate = Activation()
                activate.user = user
                activate.code = code
                activate.email = user.email
                activate.save()

                send_activation_email(request, user.email, code)
                messages.success(request, _('Account created successfully. To activate the account, follow the link sent to the mail.'))
            else: 
                messages.success(request, _('Account created successfully!'))
            return redirect('account:sign_in')
        else:
            context['signupForm'] = form
            return render(request, 'account/signup.html', context)

class LoginView(GuestOnlyView, View):
    def get(self, request):
        return render(request, 'account/signin.html')
    
    def post(self, request):
        context = {}
        form = signinForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        else:
                context['signinForm'] = form
            
        return render(request, 'account/signin.html', context)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(settings.LOGIN_REDIRECT_URL)


class ActivateView(View):
    @staticmethod
    def get(request, code):
        activate = get_object_or_404(Activation, code=code)
        user = activate.user
        user.is_active = True
        user.save()
        activate.delete()
        messages.success(request, _('You have successfully activated your account!'))
        return redirect('account:sign_in')

        
class RestoreProfileView(GuestOnlyView, View):
    def get(self, request):
        return render(request, 'account/restoreProfile.html')

class RemindUsernameView(GuestOnlyView, View):
    def get(self, request):
        return render(request, 'account/restoreProfile/remind_username.html')

    def post(self, request):
        context = {}
        form = RemindUsernameForm(request.POST)
        if form.is_valid():
            user = form.user_cache
            send_userNameForgot_email(user.email, user.username)
            messages.success(self.request, _('Your username has been successfully sent to your email.'))
            return redirect('account:sign_in')
        else:
            context['RemindUsernameForm'] = form
        return render(request, 'account/restoreProfile/remind_username.html', context)

class RestorePasswordView(GuestOnlyView, View):
    def get(self, request):
        return render(request, 'account/restoreprofile/restore_password.html')

    def post(self, request):
        context = {}
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            user = form.user_cache
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            if isinstance(uid, bytes):
                uid = uid.decode()
            send_passwordReset_email(self.request, user.email, token, uid)
            return redirect('account:restore_password_emailDone')
        else:
            context['RestorePasswordForm'] = form
        return render(request, 'account/restoreprofile/restore_password.html', context)

class RestorePasswordEmailDoneView(View):

    def get(self, request):
        return render(request, 'account/restoreProfile/restore_password_emailDone.html')

class ResendActivationCodeView(GuestOnlyView, View):

    def get(self, request):
        return render(request, 'account/restoreProfile/resend_activation_code.html')

    def post(self, request):
        context = {}
        form = ResendActivationCodeForm(request.POST)
        if form.is_valid():
            user = form.user_cache
            activation = Activation.objects.get(user=user)
            activation.delete

            code = get_random_string(20)
            activate = Activation()
            activate.code = code
            activate.user = user
            activate.save()

            send_activation_email(self.request, user.email, code)
            messages.success(self.request, _('A new activation code has been sent to your email address.'))
            return redirect('account:sign_in')
        else:
            context['ResendActivationCodeForm'] = form
            return render(request, 'account/restoreprofile/resend_activation_code.html', context)

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        user = request.user
        context['id']         = user.id
        context['username']   = user.username
        context['email']      = user.email
        context['profilePic'] = user.profile_image.url
        
        return render(request, 'account/profile.html', context)

def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        print("exception: " + str(e))
        print('eh')
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
        return None


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString, user)
            img = cv2.imread(url)
            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0
            crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]
            cv2.imwrite(url, crop_img)
            user.profile_image.delete()
            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()
            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url
            s = os.path.dirname(url)
            os.remove(url)
            os.rmdir(s)
        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)

        return HttpResponse(json.dumps(payload), content_type="application/json")

class EditProfileView(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        form = ProfileUpdateForm(instance=request.user,
				initial={
                    "id"   : request.user.id,
					"email": request.user.email, 
					"username": request.user.username,
					"profile_image": request.user.profile_image,
				}
			)
        context['form'] = form
        context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
        return render(request, 'account/profile/edit_profile.html', context)
    
    def post(self, request):
        context = {}
        user = UrlUser.objects.get(username=request.user.username)
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account:profile')
        else:
            form = ProfileUpdateForm(request.POST, instance=request.user,
				initial={
                    "id"   : request.user.id,
					"email": request.user.email, 
					"username": request.user.username,
					"profile_image": request.user.profile_image,
				}
			)
            context['form'] = form
            context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
            return render(request, 'account/profile/edit_profile.html', context)


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'account/profile/change_password.html'
    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(self.request, _('Your password was changed.'))

        return redirect('account:profile')

class DeleteProfileView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        user = request.user
        context['id']         = user.id
        context['username']   = user.username
        return render(request, 'account/profile/delete_profile.html', context)
    
    def post(self, request):  
            password = request.POST.get('pwd')
            user = authenticate(email=request.user.email, password=password)
            if user:
                profileFolder = 'profile_image'
                loc = os.path.join(settings.MEDIA_ROOT, profileFolder)
                exactLoc= os.path.join(loc, str(user.pk))
                filename = os.path.join(exactLoc, 'profile_image.png')
                os.remove(filename)
                os.rmdir(exactLoc)
                user.delete()
                messages.success(request, "Your account deleted successfully")  
                return redirect('account:sign_up')          
            else:
                messages.error(request, "Please provide correct password")  
                return redirect('account:delete_profile')