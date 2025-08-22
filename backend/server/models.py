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
