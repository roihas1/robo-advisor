from django.urls import path

from data_mgmt import views
from .views import *


urlpatterns = [
    # Investment
    path('get_plot_data/<str:type_of_graph>/', views.get_specific_plot, name='get_specific_plot'),
    path('update_all_tables/', views.update_all_tables, name='update_all_tables')
    ]
