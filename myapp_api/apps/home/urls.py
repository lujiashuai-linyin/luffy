from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path('banner/$', views.BannerListAPIView.as_view()),
    re_path('nav/header/', views.HeaderNavListAPIView.as_view()),
    re_path('nav/footer/', views.FooterNavListAPIView.as_view()),
]
