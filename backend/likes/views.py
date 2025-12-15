from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .serializers import LikesSerializer
from .models import Like
from music.models import Music

# Create your views here.
class MusicLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, music_id):
        music = get_object_or_404(Music, pk=music_id)
        # 좋아요 생성
        like, created = Like.objects.get_or_create(
            music=music,
            account=request.user
        )
        serializer = LikesSerializer(like)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def delete(self, request, music_id):
        music = get_object_or_404(Music, pk=music_id)
        like = Like.objects.filter(music=music, account=request.user).first()
        if like:
            like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, music_id):
        music = get_object_or_404(Music, pk=music_id)
        like = Like.objects.filter(music=music, account=request.user).first()
        if like:
            serializer = LikesSerializer(like)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)