from django.db import models
from music.models import Music
from django.conf import settings

# Create your models here.
class Like(models.Model):
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='likes')
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('music', 'account')

    def __str__(self):
        return f"{self.account} likes {self.music.music_name}"