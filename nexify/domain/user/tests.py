import uuid

from django.db.models.manager import Manager
from django.test import TestCase

from .models import (
    User,
    UserBasePermissions,
    UserFactory,
    UserFollow,
    UserFollowFactory,
    UserFollowID,
    UserID,
    UserManagerAutoID,
    UserPersonalData,
)
from .services import UserFollowServices, UserServices


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

        self.second_user_personal_data = UserPersonalData(
            email="random_user@email.com",
            username="random_user@email.com",
            first_name="Random",
            last_name="User",
        )
        self.second_user_base_permissions = self.user_base_permissions

        self.second_user_obj = (
            UserServices()
            .get_user_factory()
            .build_entity_with_id(
                password=self.user_password,
                personal_data=self.second_user_personal_data,
                base_permissions=self.second_user_base_permissions,
            )
        )
        self.second_user_obj.save()

        self.user_follow_obj = (
            UserFollowServices()
            .get_user_follow_factory()
            .build_entity_with_id(
                follower=self.user_obj, following=self.second_user_obj
            )
        )
        self.user_follow_obj.save()

    def test_build_user_id(self):
        user_id = UserID()
        self.assertEqual(type(user_id), UserID)

    def test_user_instance(self):
        self.assertIsInstance(self.user_obj, User)

    def test_build_user_follow_id(self):
        user_follow_id = UserFollowID(value=uuid.uuid4())
        self.assertEqual(type(user_follow_id), UserFollowID)

    def test_user_follow_instance(self):
        self.assertIsInstance(self.user_follow_obj, UserFollow)


class UserServicesTests(TestCase):
    def test_get_user_repo(self):
        user_repo = UserServices().get_user_repo()
        self.assertEqual(UserManagerAutoID[User], type(user_repo))

    def test_get_user_factory(self):
        user_factory = UserServices().get_user_factory()
        self.assertEqual(UserFactory, user_factory)


class UserFollowServicesTests(TestCase):
    def test_get_user_follow_repo(self):
        user_follow_repo = UserFollowServices().get_user_follow_repo()
        self.assertEqual(Manager[UserFollow], type(user_follow_repo))

    def test_get_user_follow_factory(self):
        user_follow_factory = UserFollowServices().get_user_follow_factory()
        self.assertEqual(UserFollowFactory, user_follow_factory)
