from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from nexify.application.user.services import UserAppServices, UserFollowAppServices
from nexify.infrastructure.custom_response.response_and_error import APIResponse
from utils.django.exceptions import (
    CannotFollowSelfException,
    InvalidPasswordException,
    UserAlreadyExistsException,
    UserFollowNotFoundException,
    UserNotFoundException,
)

from . import open_api
from .pagination import UserPagination
from .serializers import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserFollowersSerializer,
    UserFollowingSerializer,
    UserFollowRequestsSerializer,
    UserFollowSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserSignUpSerializer,
    UserUpdateSerializer,
)


@extend_schema_view(
    sign_up=open_api.user_sign_up_extension,
    login=open_api.user_login_extension,
    list=open_api.user_list_extension,
    retrieve=open_api.user_retrieve_extension,
    update_user=open_api.user_update_extension,
    delete_user=open_api.user_delete_extension,
    follow_unfollow_user=open_api.user_follow_unfollow_extension,
    accept_follow_request=open_api.accept_follow_request_extension,
    follow_requests=open_api.user_follow_requests_extension,
    followers=open_api.user_followers_extension,
    following=open_api.user_following_extension,
    delete_follow_request=open_api.delete_follow_request_extension,
    forgot_password=open_api.user_forgot_password_extension,
    reset_password=open_api.user_reset_password_extension,
)
class UserViewSet(viewsets.ViewSet):
    """
    The UserViewSet class is a viewset that provides API endpoints for managing user-related operations.

    Attributes:
        authentication_classes (tuple): A tuple of authentication classes used for user authentication.
        permission_classes (tuple): A tuple of permission classes used for user authorization.
        pagination_class (UserPagination): An instance of the UserPagination class used for pagination.

    Methods:
        initial(request, *args, **kwargs): Performs initial setup for the viewset based on the requested action.
        get_queryset(): Retrieves the queryset of active users, ordered by creation date.
        get_serializer_class(): Returns the appropriate serializer class based on the requested action.
        sign_up(request): Handles the sign up action and creates a new user.
        login(request): Handles the login action and authenticates the user.
        list(request): Retrieves a paginated list of all users, excluding the current user.
        retrieve(request, pk): Retrieves the data of a specific user.
        update_user(request): Updates the information of the current user.
        delete_user(request): Deletes the current user's account.
        follow_unfollow_user(request, pk): Follows or unfollows a user based on the provided user ID.
        accept_follow_request(request, pk): Accepts a follow request from a user based on the provided user ID.
        delete_follow_request(request, pk): Deletes a follow request from a user based on the provided user ID.
        follow_requests(request): Retrieves a list of follow requests for the current user.
        followers(request): Retrieves a list of followers for the current user.
        following(request): Retrieves a list of users that the current user is following.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = UserPagination

    exception_tuple = (
        UserAlreadyExistsException,
        UserNotFoundException,
        UserFollowNotFoundException,
        CannotFollowSelfException,
        InvalidPasswordException,
    )

    def initial(self, request, *args, **kwargs):
        """
        Performs initial setup for the viewset based on the requested action.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.

        """
        if self.action == "sign_up":
            self.authentication_classes = []
            self.permission_classes = []
        if self.action == "login":
            self.authentication_classes = []
            self.permission_classes = []
        if self.action == "forgot_password":
            self.authentication_classes = []
            self.permission_classes = []
        if self.action == "reset_password":
            self.authentication_classes = []
            self.permission_classes = []
        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        """
        Retrieves the queryset of active users, ordered by creation date.

        Returns:
            QuerySet: The queryset of active users, ordered by creation date.
        """
        user_app_services = UserAppServices()
        return user_app_services.list_users().order_by("?").exclude(is_superuser=True)

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the requested action.

        Returns:
            Serializer: The appropriate serializer class based on the requested action.
        """
        if self.action == "sign_up":
            return UserSignUpSerializer
        if self.action == "login":
            return UserLoginSerializer
        if self.action == "list":
            return UserSerializer
        if self.action == "retrieve":
            return UserSerializer
        if self.action == "update_user":
            return UserUpdateSerializer
        if self.action == "follow_requests":
            return UserFollowRequestsSerializer
        if self.action == "followers":
            return UserFollowersSerializer
        if self.action == "following":
            return UserFollowingSerializer
        if self.action == "forgot_password":
            return ForgotPasswordSerializer
        if self.action == "reset_password":
            return ResetPasswordSerializer

    @action(detail=False, methods=["post"], name="sign_up")
    def sign_up(self, request):
        """
        Handles the sign up action and creates a new user.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                user_app_services = UserAppServices()
                user_obj = user_app_services.create_user_from_dict(
                    data=serializer_data.data
                )
                serialized_data = UserSerializer(instance=user_obj)
                return APIResponse(
                    status_code=status.HTTP_201_CREATED,
                    data=serialized_data.data,
                    message="You have successfully signed up.",
                )
            except self.exception_tuple as e:
                return APIResponse(
                    status_code=e.status_code,
                    errors=e.error_data(),
                    message=e.message,
                    for_error=True,
                )
            except Exception as e:
                return APIResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=e,
                    for_error=True,
                    general_error=True,
                )
        return APIResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer_data.errors,
            message="Invalid data.",
            for_error=True,
        )

    @action(detail=False, methods=["post"], name="login")
    def login(self, request):
        """
        Handles the login action and authenticates the user.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.
        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            email = serializer_data.data.get("email", None)
            password = serializer_data.data.get("password", None)
            try:
                user = authenticate(email=email, password=password)
                unauthorized_status_code = status.HTTP_401_UNAUTHORIZED
                error_message = None
                if not user:
                    error_message = (
                        "Authentication failed. Please check your email and password."
                    )
                elif not user.is_active:
                    error_message = "Your account is not active. Please contact support for assistance."
                if error_message:
                    return APIResponse(
                        status_code=unauthorized_status_code,
                        message=error_message,
                        for_error=True,
                    )
                user_app_services = UserAppServices()
                response_data = user_app_services.get_user_data_with_token(user=user)
                return APIResponse(data=response_data, message="Login successful.")
            except Exception as e:
                return APIResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=e,
                    for_error=True,
                    general_error=True,
                )
        return APIResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer_data.errors,
            message="Invalid credentials.",
            for_error=True,
        )

    def list(self, request):
        """
        Retrieves a paginated list of all users, excluding the current user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            Exception: If an error occurs during the retrieval process.

        """
        try:
            serializer = self.get_serializer_class()
            queryset = self.get_queryset().exclude(id=str(self.request.user.id))
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serialized_data = serializer(paginated_queryset, many=True)
            paginated_data = paginator.get_paginated_response(serialized_data.data).data
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=paginated_data,
                message="All users listed successfully.",
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    def retrieve(self, request, pk):
        """
        Retrieves the data of a specific user.

        Parameters:
            request (HttpRequest): The HTTP request object.
            pk (int): The ID of the user to retrieve.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            Exception: If an error occurs during the retrieval process.

        """
        serializer = self.get_serializer_class()
        try:
            user_app_services = UserAppServices()
            user_obj = (
                user_app_services.list_users().filter(id=pk, is_active=True).first()
            )
            if user_obj:
                serialized_data = serializer(instance=user_obj)
                return APIResponse(
                    status_code=status.HTTP_200_OK,
                    data=serialized_data.data,
                    message="User data retrieved successfully.",
                )
            else:
                return APIResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="User not found.",
                    errors={},
                    for_error=True,
                )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=False, methods=["patch"], name="update_user")
    def update_user(self, request):
        """
        Updates the information of the current user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            UserAlreadyExistsException: If the user already exists.
            UserNotFoundException: If the user is not found.
            UserFollowNotFoundException: If the user to follow is not found.
            CannotFollowSelfException: If the user tries to follow themselves.
            Exception: If an error occurs during the update process.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                user_app_services = UserAppServices()
                user_obj = user_app_services.update_user_from_dict(
                    user_obj=self.request.user, data=serializer_data.data
                )
                serialized_data = UserSerializer(instance=user_obj)
                return APIResponse(
                    status_code=status.HTTP_200_OK,
                    data=serialized_data.data,
                    message="Your information has been updated successfully.",
                )
            except self.exception_tuple as e:
                return APIResponse(
                    status_code=e.status_code,
                    errors=e.error_data(),
                    message=e.message,
                    for_error=True,
                )
            except Exception as e:
                return APIResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=e,
                    for_error=True,
                    general_error=True,
                )
        return APIResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer_data.errors,
            message="Invalid data.",
            for_error=True,
        )

    @action(detail=False, methods=["delete"], name="delete_user")
    def delete_user(self, request):
        """
        Deletes the current user's account.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code and message.

        Raises:
            Exception: If an error occurs during the deletion process.

        """
        try:
            user_app_services = UserAppServices()
            user_app_services.delete_user(user_obj=self.request.user)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="Your account has been successfully deleted.",
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=True, methods=["put"], name="follow_unfollow_user")
    def follow_unfollow_user(self, request, pk):
        """
        Follows or unfollows a user based on the provided user ID.

        Parameters:
            request (HttpRequest): The HTTP request object.
            pk (int): The ID of the user to follow or unfollow.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            UserAlreadyExistsException: If the user already exists.
            UserNotFoundException: If the user is not found.
            UserFollowNotFoundException: If the user to follow is not found.
            CannotFollowSelfException: If the user tries to follow themselves.
            Exception: If an error occurs during the follow or unfollow process.
        """
        try:
            user_follow_app_services = UserFollowAppServices()
            following_user_obj, action_message = (
                user_follow_app_services.follow_or_unfollow_user(
                    user=self.request.user, following_user_id=str(pk)
                )
            )
            serialized_data = UserSerializer(instance=following_user_obj)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message=action_message,
            )
        except self.exception_tuple as e:
            return APIResponse(
                status_code=e.status_code,
                errors=e.error_data(),
                message=e.message,
                for_error=True,
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=True, methods=["put"], name="accept_follow_request")
    def accept_follow_request(self, request, pk):
        """
        Accepts a follow request from a user based on the provided user ID.

        Parameters:
            request (HttpRequest): The HTTP request object.
            pk (int): The ID of the user who sent the follow request.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            UserAlreadyExistsException: If the user already exists.
            UserNotFoundException: If the user is not found.
            UserFollowNotFoundException: If the user to follow is not found.
            CannotFollowSelfException: If the user tries to follow themselves.
            Exception: If an error occurs during the acceptance process.

        """
        try:
            user_follow_app_services = UserFollowAppServices()
            user_follow_obj = user_follow_app_services.accept_follow_request_of_user(
                user=self.request.user, follower_user_id=str(pk)
            )
            serialized_data = UserFollowSerializer(instance=user_follow_obj)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message="Follow request accepted.",
            )
        except self.exception_tuple as e:
            return APIResponse(
                status_code=e.status_code,
                errors=e.error_data(),
                message=e.message,
                for_error=True,
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=True, methods=["delete"], name="delete_follow_request")
    def delete_follow_request(self, request, pk):
        """
        Deletes a follow request from a user based on the provided user ID.

        Parameters:
            request (HttpRequest): The HTTP request object.
            pk (int): The ID of the user whose follow request will be deleted.

        Returns:
            APIResponse: The API response object containing the status code and message.

        Raises:
            UserAlreadyExistsException: If the user already exists.
            UserNotFoundException: If the user is not found.
            UserFollowNotFoundException: If the user to follow is not found.
            CannotFollowSelfException: If the user tries to follow themselves.
            Exception: If an error occurs during the deletion process.
        """
        try:
            user_follow_app_services = UserFollowAppServices()
            user_follow_app_services.delete_follow_request_of_user(
                user=self.request.user, follower_user_id=str(pk)
            )
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="Follow request deleted.",
            )
        except self.exception_tuple as e:
            return APIResponse(
                status_code=e.status_code,
                errors=e.error_data(),
                message=e.message,
                for_error=True,
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=False, methods=["get"], name="follow_requests")
    def follow_requests(self, request):
        """
        Retrieves a list of follow requests for the current user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            Exception: If an error occurs during the retrieval process.

        """
        try:
            serializer = self.get_serializer_class()
            user_follow_app_services = UserFollowAppServices()
            queryset = user_follow_app_services.follow_requests_list(
                user=self.request.user
            )
            serialized_data = serializer(queryset, many=True)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message="Follow requests listed successfully.",
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=False, methods=["get"], name="followers")
    def followers(self, request):
        """
        Retrieves a list of followers for the current user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            Exception: If an error occurs during the retrieval process.

        """
        try:
            serializer = self.get_serializer_class()
            user_follow_app_services = UserFollowAppServices()
            queryset = user_follow_app_services.user_followers(user=self.request.user)
            serialized_data = serializer(queryset, many=True)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message="Followers listed successfully.",
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=False, methods=["get"], name="following")
    def following(self, request):
        """
        Retrieves a list of users that the current user is following.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code, data, and message.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        try:
            serializer = self.get_serializer_class()
            user_follow_app_services = UserFollowAppServices()
            queryset = user_follow_app_services.user_following(user=self.request.user)
            serialized_data = serializer(queryset, many=True)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message="Following listed successfully.",
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    @action(detail=False, methods=["post"], name="forgot_password")
    def forgot_password(self, request):
        """
        Handles the forgot password action and sends password reset instructions to the user's email.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code and message.

        Raises:
            Exception: If an error occurs during the password reset process.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                user_app_services = UserAppServices()
                user_app_services.forgot_password(data=serializer_data.data)
                return APIResponse(
                    status_code=status.HTTP_200_OK,
                    message="Password reset instructions will be sent if the email is recognized.",
                )
            except self.exception_tuple as e:
                return APIResponse(
                    status_code=e.status_code,
                    errors=e.error_data(),
                    message=e.message,
                    for_error=True,
                )
            except Exception as e:
                return APIResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=e,
                    for_error=True,
                    general_error=True,
                )
        return APIResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer_data.errors,
            message="Invalid data.",
            for_error=True,
        )

    @action(detail=False, methods=["post"], name="reset_password")
    def reset_password(self, request):
        """
        Resets the password for the current user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            APIResponse: The API response object containing the status code and message.

        Raises:
            UserAlreadyExistsException: If the user already exists.
            UserNotFoundException: If the user is not found.
            UserFollowNotFoundException: If the user to follow is not found.
            CannotFollowSelfException: If the user tries to follow themselves.
            Exception: If an error occurs during the password reset process.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                user_app_services = UserAppServices()
                is_password_reset = user_app_services.reset_password(
                    data=serializer_data.data
                )
                if not is_password_reset:
                    return APIResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        message="Password reset failed. Please try again.",
                        for_error=True,
                    )
                return APIResponse(
                    status_code=status.HTTP_200_OK,
                    message="Your password has been reset successfully.",
                )
            except self.exception_tuple as e:
                return APIResponse(
                    status_code=e.status_code,
                    errors=e.error_data(),
                    message=e.message,
                    for_error=True,
                )
            except Exception as e:
                return APIResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=e,
                    for_error=True,
                    general_error=True,
                )
        return APIResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer_data.errors,
            message="Invalid data.",
            for_error=True,
        )
