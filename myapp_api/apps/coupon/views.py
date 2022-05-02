from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserCoupon
from .serializers import UserCouponModelSerializer
class UserCouponAPIVew(ListAPIView):
    """我的优惠券"""
    serializer_class = UserCouponModelSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return UserCoupon.objects.filter(is_show=True, is_deleted=False, is_use=False, user_id=self.request.user.id)
