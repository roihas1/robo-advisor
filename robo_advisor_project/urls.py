import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('watchlist/', include('watchlist.urls')),
    # More URLs modules
    # path('accounts/', include('accounts.urls')),
    # path('accounts/', include('allauth.urls')),
    path('our_core/', include('our_core.urls')),
    path('data_mgmt/', include('data_mgmt.urls')),
    path('users/', include('users.urls')),
    path('', include('investment.urls')),
    path('', include('watchlist.urls')),
    # Third party apps
    path('__debug__', include(debug_toolbar.urls)),

    path('api/', include('investment.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
