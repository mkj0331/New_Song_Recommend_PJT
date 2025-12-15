from django.db import models
from django.conf import settings
from music.models import Music

# Create your models here.
class Playlist(models.Model):
    name = models.CharField(max_length=100)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.account})"

class PlaylistMusic(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_musics')
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='in_playlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'music')

    def __str__(self):
        return f"{self.playlist.name} - {self.music.music_name}"