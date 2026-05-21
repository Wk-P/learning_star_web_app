from django.db import models
from django.conf import settings

MEDIA_TYPES = [('video', '视频'), ('audio', '音频'), ('pdf', 'PDF')]


class MediaPermission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_permissions',
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    root_dir = models.CharField(max_length=256)

    class Meta:
        unique_together = [('user', 'media_type', 'root_dir')]

    def __str__(self):
        return f'{self.user.username} → {self.media_type}:{self.root_dir}'
