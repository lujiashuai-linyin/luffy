from django.shortcuts import render
from .serializers import CourseCategoryModelSerializer, CourseModelSerializer, CourseRetrieveModelSerializer
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .paginations import CoursePageNumberPagination
from .models import CourseCategory
from .models import Course
# Create your views here.

class CourseCategoryListAPIView(ListAPIView):
    serializer_class = CourseCategoryModelSerializer
    queryset = CourseCategory.objects.filter(is_show=True, is_deleted=False).order_by('orders', '-id')

class CourseListAPIView(ListAPIView):
    serializer_class = CourseModelSerializer
    queryset = Course.objects.filter(is_show=True, is_deleted=False).order_by("orders","-id")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['course_category', ]
    ordering_fields = ('id', 'students', 'price')
    pagination_class = CoursePageNumberPagination

class CourseRetrieveAPIView(RetrieveAPIView):
    queryset = Course.objects.filter(is_show=True, is_deleted=False).order_by("orders","-id")
    serializer_class = CourseRetrieveModelSerializer

from rest_framework.generics import ListAPIView
from .models import CourseChapter
from .serializers import CourseChapterModelSerializer
from django_filters.rest_framework import DjangoFilterBackend

class CourseChapterListAPIView(ListAPIView):
    queryset = CourseChapter.objects.filter(is_show=True, is_deleted=False).order_by("orders","id")
    serializer_class = CourseChapterModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['course']