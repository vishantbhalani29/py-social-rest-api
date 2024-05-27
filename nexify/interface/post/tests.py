import uuid

from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nexify.domain.post.models import PostCommentFactory, PostFactory
from nexify.domain.user.models import UserBasePermissions, UserPersonalData
from nexify.domain.user.services import UserServices

from .views import PostCommentViewSet, PostViewSet


class PostViewSetTests(APITestCase):
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

        cls.factory = APIRequestFactory()
        cls.post_view_set = PostViewSet

        cls.expected_response_fields = ["success", "message", "data"]
        cls.expected_response_fields_with_errors = cls.expected_response_fields + [
            "errors"
        ]

    def test_list(self):
        request = self.factory.get("/api/v0/posts/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"get": "list"})(request)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.get("/api/v0/posts/")
        response = self.post_view_set.as_view({"get": "list"})(request)
        self.assertEquals(response.status_code, 401)

    def test_create(self):
        data = dict(description="Test post")

        request = self.factory.post("/api/v0/posts/", data)
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"post": "create"})(request)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.post("/api/v0/posts/", data)
        response = self.post_view_set.as_view({"post": "create"})(request)
        self.assertEquals(response.status_code, 401)

    def test_retrieve(self):
        request = self.factory.get(f"/api/v0/posts/{self.post_obj_01.id}/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"get": "retrieve"})(
            request, pk=str(self.post_obj_01.id)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.get(f"/api/v0/posts/{self.post_obj_01.id}/")
        response = self.post_view_set.as_view({"get": "retrieve"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 401)

        # With random post id
        post_id = str(uuid.uuid4())
        request = self.factory.get(f"/api/v0/posts/{post_id}/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"get": "retrieve"})(request, pk=post_id)

        self.assertEquals(response.status_code, 404)

    def test_update_post(self):
        data = dict(description="Post updated")
        request = self.factory.patch(
            f"/api/v0/posts/{self.post_obj_01.id}/update_post/", data
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"patch": "update_post"})(
            request, pk=str(self.post_obj_01.id)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.patch(
            f"/api/v0/posts/{self.post_obj_01.id}/update_post/", data
        )
        response = self.post_view_set.as_view({"patch": "update_post"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 401)

        # With random post id
        post_id = str(uuid.uuid4())
        data = dict(description="Post updated")
        request = self.factory.patch(f"/api/v0/posts/{post_id}/update_post/", data)
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"patch": "update_post"})(
            request, pk=post_id
        )
        self.assertEquals(response.status_code, 404)

        # With random user
        data = dict(description="Post updated")
        request = self.factory.patch(
            f"/api/v0/posts/{self.post_obj_01.id}/update_post/", data
        )
        force_authenticate(request=request, user=self.user_obj_02)
        response = self.post_view_set.as_view({"patch": "update_post"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 403)

    def test_delete_post(self):
        request = self.factory.delete(
            f"/api/v0/posts/{self.post_obj_01.id}/delete_post/"
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"delete": "delete_post"})(
            request, pk=str(self.post_obj_01.id)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.delete(
            f"/api/v0/posts/{self.post_obj_01.id}/delete_post/"
        )
        response = self.post_view_set.as_view({"delete": "delete_post"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 401)

        # With random post id
        post_id = str(uuid.uuid4())
        request = self.factory.delete(f"/api/v0/posts/{post_id}/delete_post/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"delete": "delete_post"})(
            request, pk=post_id
        )
        self.assertEquals(response.status_code, 404)

        # With random user
        request = self.factory.delete(
            f"/api/v0/posts/{self.post_obj_02.id}/delete_post/"
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"delete": "delete_post"})(
            request, pk=str(self.post_obj_02.id)
        )
        self.assertEquals(response.status_code, 403)

    def test_like_unlike_post(self):
        request = self.factory.put(
            f"/api/v0/posts/{self.post_obj_01.id}/like_unlike_post/"
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"put": "like_unlike_post"})(
            request, pk=str(self.post_obj_01.id)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.put(
            f"/api/v0/posts/{self.post_obj_01.id}/like_unlike_post/"
        )
        response = self.post_view_set.as_view({"put": "like_unlike_post"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 401)

        # With random post id
        post_id = str(uuid.uuid4())
        request = self.factory.put(f"/api/v0/posts/{post_id}/like_unlike_post/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"put": "like_unlike_post"})(
            request, pk=str(post_id)
        )
        self.assertEquals(response.status_code, 404)

    def test_report_post(self):
        request = self.factory.put(f"/api/v0/posts/{self.post_obj_01.id}/report_post/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"put": "report_post"})(
            request, pk=str(self.post_obj_01.id)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.put(f"/api/v0/posts/{self.post_obj_01.id}/report_post/")
        response = self.post_view_set.as_view({"put": "report_post"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 401)

        # With random post id
        post_id = str(uuid.uuid4())
        request = self.factory.put(f"/api/v0/posts/{post_id}/report_post/")
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_view_set.as_view({"put": "report_post"})(
            request, pk=post_id
        )
        self.assertEquals(response.status_code, 404)


class PostCommentViewSetTests(APITestCase):
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

        cls.post_comment_obj_01 = PostCommentFactory().build_entity_with_id(
            post=cls.post_obj_01, user=cls.user_obj_01, description="Test post comment"
        )
        cls.post_comment_obj_01.save()

        cls.factory = APIRequestFactory()
        cls.post_comment_view_set = PostCommentViewSet

        cls.expected_response_fields = ["success", "message", "data"]
        cls.expected_response_fields_with_errors = cls.expected_response_fields + [
            "errors"
        ]

    def test_create(self):
        data = dict(description="Test comment")
        request = self.factory.post(
            f"/api/v0/post_comments/?post_id={str(self.post_obj_01.id)}",
            data=data,
            format="json",
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_comment_view_set.as_view({"post": "create"})(request)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.post(
            f"/api/v0/post_comments/?post_id={str(self.post_obj_01.id)}",
            data=data,
            format="json",
        )
        response = self.post_comment_view_set.as_view({"post": "create"})(request)
        self.assertEquals(response.status_code, 401)

        # Without post id
        request = self.factory.post(f"/api/v0/post_comments/", data=data)
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_comment_view_set.as_view({"post": "create"})(request)
        self.assertEquals(response.status_code, 400)

    def test_list_post_comments(self):
        request = self.factory.get(
            f"/api/v0/post_comments/{self.post_comment_obj_01.id}/list_post_comments/"
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_comment_view_set.as_view({"get": "list_post_comments"})(
            request, pk=str(self.post_obj_01.id)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.get(
            f"/api/v0/post_comments/{self.post_comment_obj_01.id}/list_post_comments/"
        )
        response = self.post_comment_view_set.as_view({"get": "list_post_comments"})(
            request, pk=str(self.post_obj_01.id)
        )
        self.assertEquals(response.status_code, 401)

    def test_delete_post_comment(self):
        request = self.factory.delete(
            f"/api/v0/post_comments/{self.post_comment_obj_01.id}/delete_post_comment/"
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_comment_view_set.as_view(
            {"delete": "delete_post_comment"}
        )(request, pk=str(self.post_comment_obj_01.id))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data.get("success"), True)
        self.assertListEqual(list(response.data.keys()), self.expected_response_fields)

        # Without authentication
        request = self.factory.delete(
            f"/api/v0/post_comments/{self.post_comment_obj_01.id}/delete_post_comment/"
        )
        response = self.post_comment_view_set.as_view(
            {"delete": "delete_post_comment"}
        )(request, pk=str(self.post_comment_obj_01.id))
        self.assertEquals(response.status_code, 401)

        # With random post comment id
        post_comment_id = str(uuid.uuid4())
        request = self.factory.delete(
            f"/api/v0/post_comments/{post_comment_id}/delete_post_comment/"
        )
        force_authenticate(request=request, user=self.user_obj_01)
        response = self.post_comment_view_set.as_view(
            {"delete": "delete_post_comment"}
        )(request, pk=str(post_comment_id))
        self.assertEquals(response.status_code, 404)

        # With different user
        request = self.factory.delete(
            f"/api/v0/post_comments/{self.post_comment_obj_01.id}/delete_post_comment/"
        )
        force_authenticate(request=request, user=self.user_obj_02)
        response = self.post_comment_view_set.as_view(
            {"delete": "delete_post_comment"}
        )(request, pk=str(self.post_comment_obj_01.id))
        self.assertEquals(response.status_code, 403)
