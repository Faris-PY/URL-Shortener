from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from main.views import HomePageView, redirect_url, toogleUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', HomePageView.as_view(), name='home'),
    path('account/', include('account.urls')),
    path('<str:url>', redirect_url, name='redirect'),
    path('urlUpdate/', toogleUpdateView, name='toogle_update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)