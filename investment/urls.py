from django.urls import path

from investment import views
from .views import ItemListCreate, ItemDetail


urlpatterns = [
    # Investment
    path('investment/history/', views.investments_list_view, name='my_investments_history'),
    path('investment/add/', views.add_investment_view, name='add_investment'),
    # Investment Portfolio
    path('profile/portfolio/', views.profile_portfolio, name='profile_portfolio'),
    path('investment/', views.investment_main, name='investments_main'),
    path('check_positive_amount/', views.check_positive_number, name='check_amount'),

    path('items/', ItemListCreate.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDetail.as_view(), name='item-detail'),
]
