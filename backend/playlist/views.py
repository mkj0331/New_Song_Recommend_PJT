from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Playlist, PlaylistMusic
from music.models import Music
from music.serializers import MusicSerializer
from .serializers import PlaylistSerializer, PlaylistMusicSerializer

class PlaylistListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        playlists = Playlist.objects.filter(account=request.user)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlaylistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(account=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaylistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)
        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data)

    def put(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)
        serializer = PlaylistSerializer(playlist, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def patch(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)
        serializer = PlaylistSerializer(playlist, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)
        playlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class PlaylistMusicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, playlist_id):
        # 해당 유저 소유의 플레이리스트인지 확인
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)
        qs = PlaylistMusic.objects.filter(playlist=playlist).select_related('music')
        serializer = PlaylistMusicSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)
        music_id = request.data.get('music')
        music = get_object_or_404(Music, id=music_id)

        playlist_music, created = PlaylistMusic.objects.get_or_create(
            playlist=playlist,
            music=music,
        )

        serializer = PlaylistMusicSerializer(playlist_music)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def delete(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, account=request.user)

        music_id = request.data.get('music')
        music = get_object_or_404(Music, id=music_id)

        PlaylistMusic.objects.filter(
            playlist=playlist,
            music=music,
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)