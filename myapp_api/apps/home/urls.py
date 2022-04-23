from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path('banner/$', views.BannerListAPIView.as_view()),
]
