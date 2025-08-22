from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Buddy, Location, Event, Attendance

class MeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class BuddySerializer(serializers.ModelSerializer):
    buddy_username = serializers.CharField(source="buddy.username", read_only=True)
    buddy_first_name = serializers.CharField(source="buddy.first_name", read_only=True)
    buddy_last_name = serializers.CharField(source="buddy.last_name", read_only=True)
    buddy_email = serializers.EmailField(source="buddy.email", read_only=True)
    class Meta:
        model = Buddy
        fields = ["id", "buddy_username", "buddy_first_name", "buddy_last_name", "buddy_email", "created_at"]

class LocationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = Location
        fields = ["username", "latitude", "longitude", "accuracy", "heading", "speed", "updated_at"]

class EventSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    class Meta:
        model = Event
        fields = [
            "id","creator_username","title","description",
            "starts_at","ends_at","place_name","latitude","longitude",
            "visibility","created_at",
        ]

class AttendanceSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source="event.id", read_only=True)
    title = serializers.CharField(source="event.title", read_only=True)
    starts_at = serializers.DateTimeField(source="event.starts_at", read_only=True)
    class Meta:
        model = Attendance
        fields = ["event_id", "title", "starts_at", "joined_at"]
        read_only_fields = fields
