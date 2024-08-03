from django.db import models
from django.utils import timezone
from users.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    body = models.CharField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, default=None)

    def mark_as_read(self):
        """Marks the notification as read by setting the read_at field."""
        self.read_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Notification for {self.user} - {self.body[:50]}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
