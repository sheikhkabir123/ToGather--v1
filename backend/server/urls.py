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

    # locations
    path('location/', views.location_update),                 # POST
    path('location/<str:username>/', views.location_of),      # GET
    path('locations/', views.buddies_locations),              # GET

    # events
    path('events/', views.events_feed),                       # GET
    path('events/create/', views.events_create),              # POST
    path('events/<int:event_id>/', views.event_detail),       # GET/PATCH/DELETE
    path('events/<int:event_id>/join/', views.event_join),    # POST
    path('events/<int:event_id>/leave/', views.event_leave),  # DELETE
    path('events/mine/', views.my_events),                    # GET
    path('events/attending/', views.my_attending),            # GET
]
