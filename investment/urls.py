from django.urls import path

from investment import views
from .views import *


urlpatterns = [
    # Investment
    path('investment/history/', views.investments_list_view, name='my_investments_history'),
    path('investment/add/', views.add_investment, name='add_investment'),
    # Investment Portfolio

    # TODO
    path('profile/portfolio/', views.profile_portfolio, name='profile_portfolio'),
    # path('investment/', views.investment_main, name='investments_main'),
    path('check_positive_amount/', views.check_positive_number, name='check_amount'),

    # from chatgpt
    # path('items/', investmentListCreate.as_view(), name='item-list-create'),
    # path('items/<int:pk>/', investmentDetail.as_view(), name='item-detail'),

    # from YouTube
    # path('investments/', investment_list),
    # path('investments/<int:id_pk>/', investment_detail)
]
