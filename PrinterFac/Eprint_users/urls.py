from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='users-register'),
    path('profile/', views.profile, name='users-profile'),
    path('passenger/', views.pass_det, name='users-pass'),
    path('passenger/search/', views.pass_search, name='users-pass-search'),
    path('host/', views.host_det, name='users-host'),
    path('host/search/', views.host_search, name='users-host-search'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
