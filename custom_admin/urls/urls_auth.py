from django.urls import path

from custom_admin.views.admin_view import LogoutView, MyLoginView

urlpatterns = [
    path("", MyLoginView.as_view(), name="admin_login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
