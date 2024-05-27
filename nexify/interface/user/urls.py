from rest_framework import routers

from nexify.interface.user.views import UserViewSet

router = routers.SimpleRouter()
router.register(r"users", UserViewSet, basename="users")
