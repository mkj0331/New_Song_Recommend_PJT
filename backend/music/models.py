from django.db import models
from pgvector.django import VectorField

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=50)
    debut_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.artist_name
    

class Genre(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    

class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Music(models.Model):
    name = models.CharField(max_length=50)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='musics')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='musics')
    lyrics = models.TextField(blank=True)
    embedding = VectorField(dimensions=1536, default=[0.0]*1536)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class MusicMood(models.Model):
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='music_moods')
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE, related_name='music_moods')
    confidence_score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('music', 'mood')

    def __str__(self):
        return f"{self.music.music_name} - {self.mood.name} ({self.confidence_score})"