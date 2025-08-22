from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Buddy, Location

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
        read_only_fields = ["username", "updated_at"]
