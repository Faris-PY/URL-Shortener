import json
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.http import HttpResponseNotFound
import validators
from validators import ValidationFailure

from account.models import Urls
from . import service

def redirect_url(request, url):
    original_url = service.load_url(request, url)
    if original_url is not None:
        return redirect(original_url)
    else:
        return  HttpResponseNotFound()

class HomePageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                urlData = Urls.objects.filter(user_id = request.user)
            except Urls.DoesNotExist:
                context = {}
            else:
                context = {
                        'urlData' : urlData, 
                        }
            return render(request, 'main/home.html', context)
        else:
            context = {}
        return render(request, 'main/home.html', context)

    def post(self, request):
        Inputurl = request.POST.get('inputurl')
        valid = validators.url(Inputurl)
        if isinstance(valid, ValidationFailure):
            messages.success(request, _('Please provide a valid url')) 
        else:
            if Urls.objects.filter(old_url=Inputurl, user_id=request.user.pk).exists():
                messages.error(request, _('Entered url already present in our server for you. Please the pasted link in below section'))
            else:
                if service.shorten(request, Inputurl):
                    messages.success(request, _('new url is created')) 
                else:
                    messages.error(request, _('Opps... Something wrong. please try after sometime'))
        return redirect('home')
        

def toogleUpdateView(request, *args, **kwargs):
    payload = {}
    if request.POST and request.user.is_authenticated:
        try:
            urlId = request.POST.get('id')
            status = request.POST.get('status')
            if status == 'true':
                status = True
                outstatus = 'true'
            else:
                status = False
                outstatus = 'false'

            urlData = Urls.objects.get(id=int(urlId))
            urlData.is_active = status
            urlData.save()
        
        except Urls.DoesNotExist:
            payload['result'] = 'error'
            payload['message'] = 'Opps... Something wrong. please try after sometime'
        else:
            payload['result'] = 'success',
            payload['status'] = outstatus,
            payload['message'] = 'status updated',
        return HttpResponse(json.dumps(payload), content_type='text/plain')
