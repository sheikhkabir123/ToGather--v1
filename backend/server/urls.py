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
    path('location/', views.location_update),                 
    path('location/<str:username>/', views.location_of),      
    path('locations/', views.buddies_locations),              

    # events
    path('events/', views.events_feed),                        
    path('events/create/', views.events_create),               
    path('events/<int:event_id>/', views.event_detail),        
    path('events/<int:event_id>/join/', views.event_join),     
    path('events/<int:event_id>/leave/', views.event_leave),   
    path('events/mine/', views.my_events),                     
    path('events/attending/', views.my_attending),             
]
