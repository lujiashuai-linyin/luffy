from rest_framework import serializers

from .models import Banner
from .models import Nav


class BannerModelSerializer(serializers.ModelSerializer):
    '''轮播广告序列化器'''

    class Meta:
        model = Banner
        fields = ['image_url', 'link']

class NavModelSerializer(serializers.ModelSerializer):
    '''导航'''
    class Meta:
        model = Nav
        fields = ['title', 'link', 'is_site']
