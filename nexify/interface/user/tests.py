import uuid

from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nexify.domain.user.models import UserBasePermissions, UserPersonalData
from nexify.domain.user.services import UserServices

from .views import UserViewSet


class UserViewSetTests(APITestCase):
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

        cls.factory = APIRequestFactory()
        cls.user_view_set = UserViewSet()

        cls.sign_up_view = UserViewSet.as_view({"post": "sign_up"})
        cls.login_view = UserViewSet.as_view({"post": "login"})
        cls.list_view = UserViewSet.as_view({"get": "list"})
        cls.retrieve_view = UserViewSet.as_view({"get": "retrieve"})
        cls.update_user_view = UserViewSet.as_view({"patch": "update_user"})
        cls.delete_user_view = UserViewSet.as_view({"delete": "delete_user"})
        cls.follow_unfollow_user_view = UserViewSet.as_view(
            {"put": "follow_unfollow_user"}
        )
        cls.accept_follow_request_view = UserViewSet.as_view(
            {"put": "accept_follow_request"}
        )
        cls.delete_follow_request_view = UserViewSet.as_view(
            {"delete": "delete_follow_request"}
        )
        cls.follow_requests_view = UserViewSet.as_view({"get": "follow_requests"})
        cls.followers_view = UserViewSet.as_view({"get": "followers"})
        cls.following_view = UserViewSet.as_view({"get": "following"})

        cls.expected_response_fields = ["success", "message", "data"]
        cls.expected_response_fields_with_errors = cls.expected_response_fields + [
            "errors"
        ]

    def test_sign_up(self):
        data = dict(
            email="test_email@email.com",
            first_name="Test",
            last_name="Email",
            password="Test@1234",
        )
        request = self.factory.post("/api/v0/users/sign_up/", data)
        response = self.sign_up_view(request)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # With existing email
        data = dict(
            email=str(self.user_obj_01.email),
            first_name="Test",
            last_name="Email",
            password="Test@1234",
        )
        request = self.factory.post("/api/v0/users/sign_up/", data)
        response = self.sign_up_view(request)
        self.assertEquals(response.status_code, 409)

    def test_login(self):
        data = dict(email=str(self.user_obj_01.email), password=str(self.user_password))
        request = self.factory.post("/api/v0/users/login/", data)
        response = self.login_view(request)
        self.assertEquals(response.data.get("success"), True)
        self.assertEquals(response.status_code, 200)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # With wrong credentials
        data = dict(email="test_mail@email.com", password=str(self.user_password))
        request = self.factory.post("/api/v0/users/login/", data)
        response = self.login_view(request)
        self.assertEquals(response.status_code, 401)

    def test_list(self):
        request = self.factory.get("/api/v0/users/")
        force_authenticate(request, self.user_obj_01)
        response = self.list_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

    def test_retrieve(self):
        request = self.factory.get(f"/api/v0/users/{self.user_obj_02.id}/")
        force_authenticate(request, self.user_obj_01)
        response = self.retrieve_view(request, pk=str(self.user_obj_02.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # With random user id
        post_id = str(uuid.uuid4())
        request = self.factory.get(f"/api/v0/users/{post_id}/")
        force_authenticate(request, self.user_obj_01)
        response = self.retrieve_view(request, pk=post_id)
        self.assertEquals(response.status_code, 400)

    def test_update_user(self):
        data = dict(first_name="Update first name")
        request = self.factory.patch("/api/v0/users/update_user/", data)
        force_authenticate(request, self.user_obj_01)
        response = self.update_user_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # With existing user email
        data = dict(email=str(self.user_obj_01.email))
        request = self.factory.patch("/api/v0/users/update_user/", data)
        force_authenticate(request, self.user_obj_01)
        response = self.update_user_view(request)
        self.assertEquals(response.status_code, 409)

    def test_delete_user(self):
        request = self.factory.delete("/api/v0/users/delete_user/")
        force_authenticate(request, self.user_obj_01)
        response = self.delete_user_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

    def test_follow_unfollow_user(self):
        request = self.factory.put(
            f"/api/v0/users/{self.user_obj_02.id}/follow_unfollow_user/"
        )
        force_authenticate(request, self.user_obj_01)
        response = self.follow_unfollow_user_view(request, pk=str(self.user_obj_02.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Follow self
        request = self.factory.put(
            f"/api/v0/users/{self.user_obj_01.id}/follow_unfollow_user/"
        )
        force_authenticate(request, self.user_obj_01)
        response = self.follow_unfollow_user_view(request, pk=str(self.user_obj_01.id))
        self.assertEquals(response.status_code, 400)

        # With random user id
        post_id = str(uuid.uuid4())
        request = self.factory.put(f"/api/v0/users/{post_id}/follow_unfollow_user/")
        force_authenticate(request, self.user_obj_01)
        response = self.follow_unfollow_user_view(request, pk=post_id)
        self.assertEquals(response.status_code, 404)

    def test_accept_follow_request(self):
        # Create follow request
        request = self.factory.put(
            f"/api/v0/users/{self.user_obj_01.id}/follow_unfollow_user/"
        )
        force_authenticate(request, self.user_obj_02)
        response = self.follow_unfollow_user_view(request, pk=str(self.user_obj_01.id))

        request = self.factory.put(
            f"/api/v0/users/{self.user_obj_02.id}/accept_follow_request/"
        )
        force_authenticate(request, self.user_obj_01)
        response = self.accept_follow_request_view(request, pk=str(self.user_obj_02.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # With random user id
        post_id = str(uuid.uuid4())
        request = self.factory.put(f"/api/v0/users/{post_id}/accept_follow_request/")
        force_authenticate(request, self.user_obj_01)
        response = self.accept_follow_request_view(request, pk=post_id)
        self.assertEquals(response.status_code, 404)

    def test_delete_follow_request(self):
        # Create follow request
        request = self.factory.put(
            f"/api/v0/users/{self.user_obj_01.id}/follow_unfollow_user/"
        )
        force_authenticate(request, self.user_obj_02)
        response = self.follow_unfollow_user_view(request, pk=str(self.user_obj_01.id))

        request = self.factory.delete(
            f"/api/v0/users/{self.user_obj_02.id}/delete_follow_request/"
        )
        force_authenticate(request, self.user_obj_01)
        response = self.delete_follow_request_view(request, pk=str(self.user_obj_02.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # With random user id
        post_id = str(uuid.uuid4())
        request = self.factory.delete(f"/api/v0/users/{post_id}/delete_follow_request/")
        force_authenticate(request, self.user_obj_01)
        response = self.delete_follow_request_view(request, pk=post_id)
        self.assertEquals(response.status_code, 404)

    def test_follow_requests(self):
        request = self.factory.get("/api/v0/users/follow_requests/")
        force_authenticate(request, self.user_obj_01)
        response = self.follow_requests_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

    def test_followers(self):
        request = self.factory.get("/api/v0/users/followers/")
        force_authenticate(request, self.user_obj_01)
        response = self.followers_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

    def test_following(self):
        request = self.factory.get("/api/v0/users/following/")
        force_authenticate(request, self.user_obj_01)
        response = self.following_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)
