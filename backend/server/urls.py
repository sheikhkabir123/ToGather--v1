from django.urls import path
from . import views, auth_views

urlpatterns = [
    # health
    path('ping/', views.ping),

    # auth
    path('auth/register/', auth_views.register),
    path('auth/login/', auth_views.login),
    path('auth/me/', views.me),

    # buddies
    path('buddies/', views.buddies),
    path('buddies/<str:username>/', views.buddy_delete),

    # locations
    path('location/', views.location_update),                 # POST
    path('location/<str:username>/', views.location_of),      # GET
    path('locations/', views.buddies_locations),              # GET
]
