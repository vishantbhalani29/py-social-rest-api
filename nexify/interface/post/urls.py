from rest_framework import routers

from nexify.interface.post.views import PostCommentViewSet, PostViewSet

router = routers.SimpleRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"post_comments", PostCommentViewSet, basename="post-comments")
