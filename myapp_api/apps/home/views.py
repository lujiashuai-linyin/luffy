from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from .models import Banner
from .serializers import BannerModelSerializer
from myapp_api.settings import constants

class BannerListAPIView(ListAPIView):
    queryset = Banner.objects.filter(is_show=True, is_delete=False).order_by('-order', '-id')[:constants.BANNER_LENGTH]
    serializer_class = BannerModelSerializer
