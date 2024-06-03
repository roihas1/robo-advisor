from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.users_list),
    # path('', views.home),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    # TODO - check signup again- if needed
    path("check/email/", views.check_email, name='check_email'),
    path("check/first_name/", views.check_first_name, name='check_first_name'),
    path("check/last_name/", views.check_last_name, name='check_last_name'),
    path("check/phone_number/", views.check_phone_number, name='check_phone_number'),
    path("validate/password/", views.check_password_confirmation, name='check_password_confirmation'),
    path('login/', views.AppLoginView.as_view(), name='user_login'),
    path('login/email/check/', views.check_login_email, name='check_login_email_view'),
    path('login/custom_login_system/', views.custom_login_system, name='check_login_email_view'),

    # path('reset/email/check/', views.check_login_email_reset, name='check_login_email_reset'),
    path('logout/', views.logout_view, name='account_logout'),

    # # Profile API
    path('profile/', views.profile_main, name='profile_main'),
    # path('profile/accounts/', views.profile_account, name='profile_account'),
    # path('profile/accounts/change/details/', views.profile_account_details, name='profile_account_details'),
    # path('profile/accounts/change/password/', views.MyPasswordChangeForm.as_view(), name='profile_account_password'),
    #path('profile/investor/', views.profile_investor, name='profile_investor'),
]
urlpatterns = format_suffix_patterns(urlpatterns)