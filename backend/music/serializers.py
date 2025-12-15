from rest_framework import serializers
from .models import Music, Genre, Artist, Mood, MusicMood

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'debut_date']


class MusicListSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)

    class Meta:
        model = Music
        fields = ['id', 'music_name', 'artist']


class MusicSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    genre = GenreSerializer(read_only=True)

    class Meta:
        model = Music
        fields = ['id', 'music_name', 'artist', 'genre']