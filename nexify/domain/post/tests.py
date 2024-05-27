import uuid

from django.db.models.manager import Manager
from django.test import TestCase

from nexify.domain.user.models import UserBasePermissions, UserPersonalData
from nexify.domain.user.services import UserServices

from .models import (
    Post,
    PostComment,
    PostCommentFactory,
    PostCommentID,
    PostFactory,
    PostID,
    PostLike,
    PostLikeFactory,
    PostLikeID,
    ReportedPost,
    ReportedPostFactory,
    ReportedPostID,
)
from .services import (
    PostCommentServices,
    PostLikeServices,
    PostServices,
    ReportedPostServices,
)


class PostTests(TestCase):
    def setUp(self):
        self.user_password = "Test@1234"
        self.user_personal_data = UserPersonalData(
            email="test_user@email.com",
            username="test_user@email.com",
            first_name="Test",
            last_name="User",
        )
        self.user_base_permissions = UserBasePermissions(is_staff=False, is_active=True)

        self.user_obj = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=self.user_password,
                personal_data=self.user_personal_data,
                base_permissions=self.user_base_permissions,
            )
        )
        self.user_obj.save()

        self.post_obj = PostFactory().build_entity_with_id(
            user=self.user_obj, description="Test post"
        )
        self.post_obj.save()

        self.post_comment_obj = PostCommentFactory().build_entity_with_id(
            post=self.post_obj, user=self.user_obj, description="Test post comment"
        )
        self.post_comment_obj.save()

        self.post_like_obj = PostLikeFactory().build_entity_with_id(
            post=self.post_obj, user=self.user_obj
        )
        self.post_like_obj.save()

        self.reported_post_obj = ReportedPostFactory().build_entity_with_id(
            post=self.post_obj, user=self.user_obj
        )
        self.reported_post_obj.save()

    def test_build_post_id(self):
        post_id = PostID(value=uuid.uuid4())
        self.assertEqual(type(post_id), PostID)

    def test_post_instance(self):
        self.assertIsInstance(self.post_obj, Post)

    def test_build_post_comment_id(self):
        post_comment_id = PostCommentID(value=uuid.uuid4())
        self.assertEqual(type(post_comment_id), PostCommentID)

    def test_post_comment_instance(self):
        self.assertIsInstance(self.post_comment_obj, PostComment)

    def test_build_post_like_id(self):
        post_like_id = PostLikeID(value=uuid.uuid4())
        self.assertEqual(type(post_like_id), PostLikeID)

    def test_post_like_instance(self):
        self.assertIsInstance(self.post_like_obj, PostLike)

    def test_build_reported_post_id(self):
        reported_post_id = ReportedPostID(value=uuid.uuid4())
        self.assertEqual(type(reported_post_id), ReportedPostID)

    def test_reported_post_instance(self):
        self.assertIsInstance(self.reported_post_obj, ReportedPost)


class PostServicesTests(TestCase):
    def test_get_post_repo(self):
        post_repo = PostServices().get_post_repo()
        self.assertEqual(Manager[Post], type(post_repo))

    def test_get_post_factory(self):
        post_factory = PostServices().get_post_factory()
        self.assertEqual(PostFactory, post_factory)

    def test_get_post_comment_repo(self):
        post_comment_repo = PostCommentServices().get_post_comment_repo()
        self.assertEqual(Manager[PostComment], type(post_comment_repo))

    def test_get_post_comment_factory(self):
        post_comment_factory = PostCommentServices().get_post_comment_factory()
        self.assertEqual(PostCommentFactory, post_comment_factory)

    def test_get_post_like_repo(self):
        post_like_repo = PostLikeServices().get_post_like_repo()
        self.assertEqual(Manager[PostLike], type(post_like_repo))

    def test_get_post_like_factory(self):
        post_like_factory = PostLikeServices().get_post_like_factory()
        self.assertEqual(PostLikeFactory, post_like_factory)

    def test_get_reported_post_repo(self):
        reported_post_repo = ReportedPostServices().get_reported_post_repo()
        self.assertEqual(Manager[ReportedPost], type(reported_post_repo))

    def test_get_reported_post_factory(self):
        reported_post_factory = ReportedPostServices().get_reported_post_factory()
        self.assertEqual(ReportedPostFactory, reported_post_factory)
