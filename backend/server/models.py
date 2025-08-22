from django.db import models
from django.contrib.auth.models import User

class Buddy(models.Model):
    user = models.ForeignKey(User, related_name='buddy_links', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, related_name='follower_links', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'buddy')

    def __str__(self):
        return f"{self.user.username} -> {self.buddy.username}"

class Location(models.Model):
    user = models.OneToOneField(User, related_name='location', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.FloatField(null=True, blank=True)
    heading = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} @ ({self.latitude}, {self.longitude})"

class Event(models.Model):
    VISIBILITY_CHOICES = [
        ("private", "Private"),
        ("buddies", "Buddies"),
        ("public", "Public"),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events_created")
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)

    place_name = models.CharField(max_length=140, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="buddies")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.creator.username}"

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")

    def __str__(self):
        return f"{self.user.username} -> {self.event.title}"
