from django.contrib import admin
from django.urls import path, include
from .views import PlaylistListView, PlaylistDetailView, PlaylistMusicView

urlpatterns = [
    path('playlists/', PlaylistListView.as_view(), name='playlist-list'),
    path('playlists/<int:playlist_id>/', PlaylistDetailView.as_view(), name='playlist-detail'),
    path('playlists/<int:playlist_id>/musics/', PlaylistMusicView.as_view()),
]