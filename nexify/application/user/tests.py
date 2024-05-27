import uuid

from django.db.models.query import QuerySet
from django.test import TestCase

from nexify.domain.user.models import (
    User,
    UserBasePermissions,
    UserFollow,
    UserPersonalData,
)
from nexify.domain.user.services import UserServices

from .services import UserAppServices, UserFollowAppServices


class UserAppServicesTests(TestCase):
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

        cls.user_app_services = UserAppServices()

    def test_list_users(self):
        user_list = self.user_app_services.list_users()
        self.assertEqual(type(user_list), QuerySet[User])

    def test_create_user_from_dict(self):
        user_obj = self.user_app_services.create_user_from_dict(
            data=dict(
                email="user_01@email.com",
                username="user_01@email.com",
                first_name="User",
                last_name="One",
            )
        )
        self.assertEqual(isinstance(user_obj, User), True)

        with self.assertRaises(Exception):
            # With existing email
            self.user_app_services.create_user_from_dict(
                data=dict(
                    email="random_user@email.com",
                    username="random_user@email.com",
                    first_name="Random",
                    last_name="User",
                )
            )

    def test_get_user_data_with_token(self):
        user_data = self.user_app_services.get_user_data_with_token(
            user=self.user_obj_01
        )
        self.assertIsInstance(user_data, dict)

    def test_update_user_from_dict(self):
        user_obj = self.user_app_services.update_user_from_dict(
            user_obj=self.user_obj_02, data=dict(first_name="Updated")
        )
        self.assertEqual(isinstance(user_obj, User), True)

        with self.assertRaises(Exception):
            # With existing email
            self.user_app_services.update_user_from_dict(
                user_obj=self.user_obj_02, data=dict(email=str(self.user_obj_01.email))
            )

    def test_delete_user(self):
        response = self.user_app_services.delete_user(user_obj=self.user_obj_02)
        self.assertIsInstance(response, bool)


class UserFollowAppServicesTests(TestCase):
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

        cls.user_follow_app_services = UserFollowAppServices()

    def test_follow_or_unfollow_user(self):
        following_user_obj, action_message = (
            self.user_follow_app_services.follow_or_unfollow_user(
                user=self.user_obj_01, following_user_id=str(self.user_obj_02.id)
            )
        )

        self.assertEqual(isinstance(following_user_obj, User), True)
        self.assertIsInstance(action_message, str)

        with self.assertRaises(Exception):
            # With same users
            self.user_follow_app_services.follow_or_unfollow_user(
                user=self.user_obj_01, following_user_id=str(self.user_obj_01.id)
            )

            # With random following user id
            self.user_follow_app_services.follow_or_unfollow_user(
                user=self.user_obj_01, following_user_id=str(uuid.uuid4())
            )

    def test_accept_follow_request_of_user(self):
        # Create follow request
        self.user_follow_app_services.follow_or_unfollow_user(
            user=self.user_obj_01, following_user_id=str(self.user_obj_02.id)
        )

        exist_user_follow_obj = (
            self.user_follow_app_services.accept_follow_request_of_user(
                user=self.user_obj_02, follower_user_id=str(self.user_obj_01.id)
            )
        )
        self.assertEqual(isinstance(exist_user_follow_obj, UserFollow), True)

        with self.assertRaises(Exception):
            # With random follower user id
            self.user_follow_app_services.accept_follow_request_of_user(
                user=self.user_obj_02, follower_user_id=str(uuid.uuid4())
            )

            # With random both users
            self.user_follow_app_services.accept_follow_request_of_user(
                user=self.user_obj_01, follower_user_id=str(uuid.uuid4())
            )

    def test_delete_follow_request_of_user(self):
        # Create follow request
        self.user_follow_app_services.follow_or_unfollow_user(
            user=self.user_obj_01, following_user_id=str(self.user_obj_02.id)
        )

        self.user_follow_app_services.delete_follow_request_of_user(
            user=self.user_obj_02, follower_user_id=str(self.user_obj_01.id)
        )

        with self.assertRaises(Exception):
            # With random follower user id
            self.user_follow_app_services.delete_follow_request_of_user(
                user=self.user_obj_02, follower_user_id=str(uuid.uuid4())
            )

            # With random both users
            self.user_follow_app_services.accept_follow_request_of_user(
                user=self.user_obj_01, follower_user_id=str(uuid.uuid4())
            )

    def test_follow_requests_list(self):
        list_follow_requests = self.user_follow_app_services.follow_requests_list(
            user=self.user_obj_01
        )
        self.assertEqual(type(list_follow_requests), QuerySet[UserFollow])

    def test_user_followers(self):
        user_followers_list = self.user_follow_app_services.user_followers(
            user=self.user_obj_01
        )
        self.assertEqual(type(user_followers_list), QuerySet[UserFollow])

    def test_user_following(self):
        user_following_list = self.user_follow_app_services.user_following(
            user=self.user_obj_01
        )
        self.assertEqual(type(user_following_list), QuerySet[UserFollow])
