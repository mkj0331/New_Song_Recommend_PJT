from rest_framework import serializers
from .models import Playlist, PlaylistMusic
from music.serializers import MusicSerializer

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PlaylistMusicSerializer(serializers.ModelSerializer):
    music = MusicSerializer(read_only=True)

    class Meta:
        model = PlaylistMusic
        fields = ['id', 'music', 'created_at']
        read_only_fields = ['id', 'created_at', 'music']