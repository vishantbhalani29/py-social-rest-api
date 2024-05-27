"""
URL configuration for nexify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from nexify.interface.post.urls import router as post_router
from nexify.interface.subscription.urls import router as subscription_router
from nexify.interface.user.social_auth.urls import router as social_auth_router
from nexify.interface.user.urls import router as user_router

API_SWAGGER_URL = settings.API_SWAGGER_URL
PROJECT_URL = "/custom_admin"
REDIRECTION_URL = API_SWAGGER_URL if settings.DEBUG else PROJECT_URL

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url=REDIRECTION_URL, permanent=False)),
]

urlpatterns += [
    path(API_SWAGGER_URL, include(user_router.urls)),
    path(API_SWAGGER_URL, include(post_router.urls)),
    path(API_SWAGGER_URL, include(subscription_router.urls)),
    # Social auth url
    path(API_SWAGGER_URL, include(social_auth_router.urls)),
    # Custom admin url
    path("custom_admin/", include("custom_admin.urls")),
]

urlpatterns += [
    path(
        API_SWAGGER_URL,
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v0/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("__debug__/", include(debug_toolbar.urls)),
]
