from django.urls import include, path

from . import urls_auth, urls_dashboard

app_name = "customadmin"
urlpatterns = [path("", include(urls_auth)), path("", include(urls_dashboard))]
