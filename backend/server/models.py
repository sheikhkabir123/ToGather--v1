from django.db import models
from django.contrib.auth.models import User

class Buddy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_links")
    buddy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "buddy")

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
