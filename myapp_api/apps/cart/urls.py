from django.urls import path,re_path
from . import views
urlpatterns = [
    path("", views.CartAPIView.as_view(
        {
            "post":"add",
            "get":"list",
            "patch":"change_selected",
            "put":"change_expire",
            "delete":"del_cart",
        }) ),
    path("order/", views.CartAPIView.as_view({"get": "get_selected_course"}))
]
