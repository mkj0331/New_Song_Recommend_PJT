from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Music
from .serializers import MusicListSerializer, MusicSerializer
from pgvector.django import MaxInnerProduct


# Create your views here.
@api_view(['GET'])
def list_musics(request):
    musics = Music.objects.order_by('-created_at')
    serialized = MusicListSerializer(musics, many=True)
    return Response(serialized)


@api_view(['GET'])
def music_details(request, music_pk):
    music = get_object_or_404(Music, pk=music_pk)
    serialized = MusicListSerializer(music, many=True)
    return Response(serialized)


@api_view(['GET'])
def recommend_based_on_music(request, music_pk):
    music = get_object_or_404(Music, pk=music_pk)
    target_vec = music.embedding
    recommended_music = Music.objects.order_by(MaxInnerProduct("embedding", target_vec).desc())[:10]
    serialized = MusicListSerializer(recommended_music, many=True)
    return Response(serialized)