from django.urls import path
from . import views
urlpatterns = [
    path(r"list/",views.UserCouponAPIVew.as_view()),
]
