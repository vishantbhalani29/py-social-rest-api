from rest_framework import routers

from nexify.interface.user.social_auth.views import SocialAuthViewSet

router = routers.SimpleRouter()
router.register(r"social_auth", SocialAuthViewSet, basename="social-auth")
