from rest_framework import serializers

from .models import Banner


class BannerModelSerializer(serializers.ModelSerializer):
    '''轮播广告序列化器'''

    class Meta:
        model = Banner
        fields = ['image_url', 'link']
