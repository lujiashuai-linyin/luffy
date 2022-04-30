from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path('category/', views.CourseCategoryListAPIView.as_view()),
    path('', views.CourseListAPIView.as_view()),
    re_path(r"(?P<pk>\d+)/", views.CourseRetrieveAPIView.as_view()),
    path(r"chapter/", views.CourseChapterListAPIView.as_view()),
]