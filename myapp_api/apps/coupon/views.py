from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserCoupon
from .serializers import UserCouponModelSerializer
class UserCouponAPIVew(ListAPIView):
    """我的优惠券"""
    queryset = UserCoupon.objects.filter(is_show=True, is_deleted=False, is_use=False)
    serializer_class = UserCouponModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering_fields = ('user_id',)
