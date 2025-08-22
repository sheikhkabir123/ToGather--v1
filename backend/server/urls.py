from django.urls import path
from . import views, auth_views

urlpatterns = [
    path('ping/', views.ping),

    # auth
    path('auth/register/', auth_views.register),
    path('auth/login/', auth_views.login),
    path('auth/me/', views.me),

    # buddies
    path('buddies/', views.buddies),
    path('buddies/<str:username>/', views.buddy_delete),
]
