from rest_framework import serializers
from .models import Like

class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['music', 'account']