from django.urls import path

from . import views

urlpatterns = [
    path("user/info/", views.user_info, name="codeforces-user-info"),
]
