import uuid

from django.db.models.query import QuerySet
from django.test import TestCase

from nexify.domain.post.models import (
    Post,
    PostComment,
    PostCommentFactory,
    PostFactory,
    ReportedPost,
)
from nexify.domain.user.models import UserBasePermissions, UserPersonalData
from nexify.domain.user.services import UserServices

from .services import PostAppServices, PostCommentAppServices, PostLikeAppServices


class PostAppServicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_password = "Test@1234"
        cls.user_personal_data_01 = UserPersonalData(
            email="test_user@email.com",
            username="test_user@email.com",
            first_name="Test",
            last_name="User",
        )
        cls.user_base_permissions_01 = UserBasePermissions(
            is_staff=False, is_active=True
        )

        cls.user_obj_01 = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=cls.user_password,
                personal_data=cls.user_personal_data_01,
                base_permissions=cls.user_base_permissions_01,
            )
        )
        cls.user_obj_01.save()

        cls.user_personal_data_02 = UserPersonalData(
            email="random_user@email.com",
            username="random_user@email.com",
            first_name="Random",
            last_name="User",
        )
        cls.user_base_permissions_02 = cls.user_base_permissions_01

        cls.user_obj_02 = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=cls.user_password,
                personal_data=cls.user_personal_data_02,
                base_permissions=cls.user_base_permissions_02,
            )
        )
        cls.user_obj_02.save()

        cls.post_obj_01 = PostFactory().build_entity_with_id(
            user=cls.user_obj_01, description="Test post one"
        )
        cls.post_obj_01.save()

        cls.post_obj_02 = PostFactory().build_entity_with_id(
            user=cls.user_obj_02, description="Test post two"
        )
        cls.post_obj_02.save()

        cls.post_app_services = PostAppServices()
        cls.post_comment_app_services = PostCommentAppServices()
        cls.post_like_app_services = PostLikeAppServices()

    def test_list_posts(self):
        post_list = self.post_app_services.list_posts()
        self.assertEqual(type(post_list), QuerySet[Post])

    def test_create_post_from_dict(self):
        post_obj = self.post_app_services.create_post_from_dict(
            user=self.user_obj_01, data=dict(description="Test post")
        )
        self.assertEqual(isinstance(post_obj, Post), True)

    def test_get_post_by_id(self):
        post_obj = self.post_app_services.get_post_by_id(
            post_id=str(self.post_obj_01.id), user=self.user_obj_01
        )
        self.assertEqual(type(post_obj), Post)

        with self.assertRaises(Exception):
            # With random post id
            self.post_app_services.get_post_by_id(
                post_id=str(uuid.uuid4()), user=self.user_obj_01
            )

    def test_update_post_from_dict(self):
        post_obj = self.post_app_services.update_post_from_dict(
            post_id=str(self.post_obj_01.id),
            user=self.user_obj_01,
            data=dict(description="Post update"),
        )
        self.assertEqual(isinstance(post_obj, Post), True)

        with self.assertRaises(Exception):
            # With random post id
            self.post_app_services.update_post_from_dict(
                post_id=str(uuid.uuid4()),
                user=self.user_obj_01,
                data=dict(description="Post update"),
            )

            # With different user
            self.post_app_services.update_post_from_dict(
                post_id=str(self.post_obj_01.id),
                user=self.user_obj_02,
                data=dict(description="Post update"),
            )

    def test_delete_post(self):
        post_obj = self.post_app_services.delete_post(
            post_id=str(self.post_obj_01.id), user=self.user_obj_01
        )
        self.assertIsInstance(post_obj, bool)

        with self.assertRaises(Exception):
            # With random post id
            self.post_app_services.delete_post(
                post_id=str(uuid.uuid4()), user=self.user_obj_01
            )

            # With different user
            self.post_app_services.delete_post(
                post_id=str(self.post_obj_01.id), user=self.user_obj_02
            )

    def test_post_reporting(self):
        reported_post_obj = self.post_app_services.post_reporting(
            post_id=str(self.post_obj_01.id), user=self.user_obj_01
        )
        self.assertEqual(isinstance(reported_post_obj, ReportedPost), True)

        with self.assertRaises(Exception):
            # With random post id
            self.post_app_services.post_reporting(
                post_id=str(uuid.uuid4()), user=self.user_obj_01
            )

            # With user who already reported same post
            # Report first time
            self.post_app_services.post_reporting(
                post_id=str(self.post_obj_01.id), user=self.user_obj_02
            )
            # Report second time
            self.post_app_services.post_reporting(
                post_id=str(self.post_obj_01.id), user=self.user_obj_02
            )


class PostCommentAppServicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_password = "Test@1234"
        cls.user_personal_data_01 = UserPersonalData(
            email="test_user@email.com",
            username="test_user@email.com",
            first_name="Test",
            last_name="User",
        )
        cls.user_base_permissions_01 = UserBasePermissions(
            is_staff=False, is_active=True
        )

        cls.user_obj_01 = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=cls.user_password,
                personal_data=cls.user_personal_data_01,
                base_permissions=cls.user_base_permissions_01,
            )
        )
        cls.user_obj_01.save()

        cls.user_personal_data_02 = UserPersonalData(
            email="random_user@email.com",
            username="random_user@email.com",
            first_name="Random",
            last_name="User",
        )
        cls.user_base_permissions_02 = cls.user_base_permissions_01

        cls.user_obj_02 = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=cls.user_password,
                personal_data=cls.user_personal_data_02,
                base_permissions=cls.user_base_permissions_02,
            )
        )
        cls.user_obj_02.save()

        cls.post_obj_01 = PostFactory().build_entity_with_id(
            user=cls.user_obj_01, description="Test post"
        )
        cls.post_obj_01.save()

        cls.post_comment_obj = PostCommentFactory().build_entity_with_id(
            post=cls.post_obj_01, user=cls.user_obj_01, description="Test post comment"
        )
        cls.post_comment_obj.save()

        cls.post_comment_app_services = PostCommentAppServices()

    def test_list_comments(self):
        comment_list = self.post_comment_app_services.list_comments()
        self.assertEqual(type(comment_list), QuerySet[PostComment])

    def test_create_post_comment(self):
        post_comment_obj = self.post_comment_app_services.create_post_comment(
            user=self.user_obj_01,
            post_id=str(self.post_obj_01.id),
            data=dict(description="Test post comment"),
        )
        self.assertEqual(isinstance(post_comment_obj, PostComment), True)

        with self.assertRaises(Exception):
            # With random post id
            self.post_comment_app_services.create_post_comment(
                user=self.user_obj_01,
                post_id=str(uuid.uuid4()),
                data=dict(description="Test post comment"),
            )

    def test_list_comments_by_post(self):
        post_comment_list = self.post_comment_app_services.list_comments_by_post(
            user=self.user_obj_01, post_id=str(self.post_obj_01.id)
        )
        self.assertEqual(type(post_comment_list), QuerySet[PostComment])

    def test_delete_comment(self):
        self.post_comment_app_services.delete_comment(
            post_comment_id=str(self.post_comment_obj.id), user=self.user_obj_01
        )

        with self.assertRaises(Exception):
            # With random post comment id
            self.post_comment_app_services.delete_comment(
                post_comment_id=str(uuid.uuid4()), user=self.user_obj_01
            )

            # With different user
            self.post_comment_app_services.delete_comment(
                post_comment_id=str(self.post_comment_obj.id), user=self.user_obj_02
            )


class PostLikeAppServicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_password = "Test@1234"
        cls.user_personal_data_01 = UserPersonalData(
            email="test_user@email.com",
            username="test_user@email.com",
            first_name="Test",
            last_name="User",
        )
        cls.user_base_permissions_01 = UserBasePermissions(
            is_staff=False, is_active=True
        )

        cls.user_obj_01 = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=cls.user_password,
                personal_data=cls.user_personal_data_01,
                base_permissions=cls.user_base_permissions_01,
            )
        )
        cls.user_obj_01.save()

        cls.post_obj_01 = PostFactory().build_entity_with_id(
            user=cls.user_obj_01, description="Test post"
        )
        cls.post_obj_01.save()

        cls.post_like_app_services = PostLikeAppServices()

    def test_like_or_unlike_post(self):
        post_obj, action_message = self.post_like_app_services.like_or_unlike_post(
            user=self.user_obj_01, post_id=str(self.post_obj_01.id)
        )

        self.assertEqual(isinstance(post_obj, Post), True)
        self.assertIsInstance(action_message, str)

        with self.assertRaises(Exception):
            # With random post id
            self.post_like_app_services.like_or_unlike_post(
                user=self.user_obj_01, post_id=str(uuid.uuid4())
            )
