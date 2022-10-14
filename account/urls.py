from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .views import (
    SignupView, LoginView, LogoutView, ActivateView, 
    RestoreProfileView, RemindUsernameView, RestorePasswordView, RestorePasswordEmailDoneView, ResendActivationCodeView,
    ProfileView, crop_image, EditProfileView, ChangePasswordView, DeleteProfileView
)
app_name = 'account'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='sign_up'),
    path('signin/', LoginView.as_view(), name='sign_in'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('activate/<code>/', ActivateView.as_view(), name='activate'),
    
    path('remind/', RestoreProfileView.as_view(), name='remind_profile'), 
    path('remind/username/', RemindUsernameView.as_view(), name='remind_username'), 
    path('resend/activation_code/', ResendActivationCodeView.as_view(), name='resend_activation_code'),
    
    path('restore/password/', RestorePasswordView.as_view(), name='restore_password'),
    path('restore/password/done', RestorePasswordEmailDoneView.as_view(), name='restore_password_emailDone'),
    path('restore/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('account:restore_password_complete'), template_name='account/restoreProfile/restore_password_confirm.html'), name='restore_password_confirm'),     
    path('restore/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/restoreProfile/restore_password_complete.html'), name='restore_password_complete'),

    path('profile/', ProfileView.as_view(), name='profile'), 
    path('editProfile/', EditProfileView.as_view(), name='edit_profile'), 
    path('editProfile/cropImage/', crop_image, name='crop_image'),
    path('changePassword/',ChangePasswordView.as_view(), name='change_password'),
    path('deleteProfile/', DeleteProfileView.as_view(), name='delete_profile'),

]