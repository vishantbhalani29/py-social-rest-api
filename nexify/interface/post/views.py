from drf_spectacular.utils import extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from nexify.application.post.services import (
    PostAppServices,
    PostCommentAppServices,
    PostLikeAppServices,
    PostRecommendationAppServices,
)
from nexify.infrastructure.custom_response.response_and_error import APIResponse
from utils.django.exceptions import (
    FileExtensionNotAllowedException,
    PostAlreadyReportedException,
    PostCommentNotFoundException,
    PostNotFoundException,
    UnauthorizedPostAccess,
    UnauthorizedPostCommentAccess,
)

from . import open_api
from .filters import PostFilters
from .pagination import PostPagination
from .serializers import (
    PostCommentCreateSerializer,
    PostCommentSerializer,
    PostCreateSerializer,
    PostSerializer,
    PostUpdateSerializer,
    ReportedPostSerializer,
)


@extend_schema_view(
    list=open_api.post_list_extension,
    create=open_api.post_create_extension,
    retrieve=open_api.post_retrieve_extension,
    update_post=open_api.post_update_extension,
    delete_post=open_api.post_delete_extension,
    like_unlike_post=open_api.post_like_unlike_extension,
    report_post=open_api.post_report_extension,
    list_recommend_posts=open_api.list_recommend_posts_extension,
)
class PostViewSet(viewsets.ViewSet):
    """
    A viewset for handling CRUD operations on posts.

    This viewset provides the following actions:
    - list: Retrieves a paginated list of posts.
    - create: Creates a new post.
    - retrieve: Retrieves a specific post.
    - update_post: Updates a specific post.
    - delete_post: Deletes a specific post.
    - like_unlike_post: Updates the like status of a specific post.
    - report_post: Reports a specific post.
    - list_recommend_posts: Retrieves a list of recommended posts.

    The viewset requires authentication and permission to perform any action.

    Attributes:
    - authentication_classes (tuple): A tuple of authentication classes required for the viewset.
    - permission_classes (tuple): A tuple of permission classes required for the viewset.
    - pagination_class (class): The pagination class to be used for paginating the list of posts.
    - filter_class (class): The filter class to be used for filtering the list of posts.

    Exceptions:
    - PostNotFoundException: Raised when a post with the provided post_id does not exist.
    - UnauthorizedPostAccess: Raised when the authenticated user does not have access to the post.
    - PostAlreadyReportedException: Raised when the post has already been reported.

    Methods:
    - get_queryset: Retrieves the queryset of posts to be used by the viewset.
    - get_serializer_class: Retrieves the serializer class to be used for serializing/deserializing data.
    - list: Handles the HTTP GET request for listing posts.
    - create: Handles the HTTP POST request for creating a new post.
    - retrieve: Retrieves a specific post.
    - update_post: Updates a specific post.
    - delete_post: Deletes a specific post.
    - like_unlike_post: Updates the like status of a specific post.
    - report_post: Reports a specific post.
    - list_recommend_posts: Retrieves a list of recommended posts.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PostPagination
    filter_class = PostFilters

    exception_tuple = (
        PostNotFoundException,
        UnauthorizedPostAccess,
        PostAlreadyReportedException,
        FileExtensionNotAllowedException,
    )

    def get_queryset(self):
        """
        Retrieves the queryset of posts to be used by the viewset.

        This method creates an instance of the PostAppServices class and calls its 'list_posts' method to retrieve a queryset of active posts. The queryset is ordered by creation date in descending order.

        Returns:
            QuerySet[Post]: A queryset of active posts, ordered by creation date in descending order.
        """
        post_app_services = PostAppServices()
        return post_app_services.list_posts()

    def get_serializer_class(self):
        """
        Retrieves the serializer class to be used for serializing/deserializing data.

        This method determines the appropriate serializer class based on the action being performed. If the action is "list", it returns the PostSerializer class. If the action is "create", it returns the PostCreateSerializer class. If the action is "retrieve", it also returns the PostSerializer class. If the action is "update_post", it returns the PostUpdateSerializer class.

        Returns:
            Serializer: The serializer class to be used for serializing/deserializing data based on the action being performed.
        """
        if self.action == "list":
            return PostSerializer
        if self.action == "create":
            return PostCreateSerializer
        if self.action == "retrieve":
            return PostSerializer
        if self.action == "update_post":
            return PostUpdateSerializer
        if self.action == "list_recommend_posts":
            return PostSerializer

    def list(self, request):
        """
        Handles the HTTP GET request for listing posts.

        This method retrieves the queryset of posts to be used by the viewset and applies filtering and pagination to the queryset. It then serializes the paginated data and returns a paginated response.

        Parameters:
        - request (HttpRequest): The HTTP GET request object.

        Returns:
        - APIResponse: An APIResponse object containing the paginated data of the posts.

        Raises:
        - Exception: If an error occurs during the listing process.

        """
        try:
            serializer = self.get_serializer_class()
            queryset = self.get_queryset()
            filtered_queryset = self.filter_class(
                self.request.query_params, queryset=queryset
            ).qs
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(filtered_queryset, request)
            serialized_data = serializer(paginated_queryset, many=True)
            paginated_data = paginator.get_paginated_response(serialized_data.data).data
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=paginated_data,
                message="All posts listed successfully.",
            )
        except Exception as e:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=e,
                for_error=True,
                general_error=True,
            )

    def create(self, request):
        """
        Handles the HTTP POST request for creating a new post.

        This method validates the request data using the serializer. If the data is valid, it creates a new post using the PostAppServices class and returns the serialized data of the created post. If the data is invalid, it returns an APIResponse object with a status code of 400 and the validation errors.

        Parameters:
        - request (HttpRequest): The HTTP POST request object.

        Returns:
        - APIResponse: An APIResponse object containing the serialized data of the created post and a success message.

        Raises:
        - FileExtensionNotAllowedException: If the file extension is not allowed.
        - Exception: If any other error occurs during the creation process.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                post_app_services = PostAppServices()
                post_obj = post_app_services.create_post_from_dict(
                    user=self.request.user,
                    data=serializer_data.data,
                    file_obj=request.data.get("file"),
                )
                serialized_data = PostSerializer(instance=post_obj)
                return APIResponse(
                    status_code=status.HTTP_201_CREATED,
                    data=serialized_data.data,
                    message="Post created successfully.",
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

    def retrieve(self, request, pk):
        """
        Retrieves a specific post.

        This method handles the HTTP GET request for retrieving a specific post. It uses the PostAppServices class to get the post object based on the provided post_id and the authenticated user. The post object is then serialized using the serializer class obtained from the get_serializer_class() method. The serialized data of the post is returned in an APIResponse object with a status code of 200 and a success message.

        Parameters:
        - request (HttpRequest): The HTTP GET request object.
        - pk (int): The primary key of the post to be retrieved.

        Returns:
        - APIResponse: An APIResponse object containing the serialized data of the retrieved post and a success message.

        Raises:
        - PostNotFoundException: If the post with the provided post_id does not exist.
        - UnauthorizedPostAccess: If the authenticated user does not have access to the post.
        - Exception: If any other error occurs during the retrieval process.

        """
        serializer = self.get_serializer_class()
        try:
            post_app_services = PostAppServices()
            post_obj = post_app_services.get_post_by_id(
                post_id=pk, user=self.request.user
            )
            serialized_data = serializer(instance=post_obj)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message="Post data retrieved successfully.",
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

    @action(detail=True, methods=["patch"], name="update_post")
    def update_post(self, request, pk):
        """
        Updates a specific post.

        This method handles the HTTP PATCH request for updating a specific post. It validates the request data using the serializer obtained from the get_serializer_class() method. If the data is valid, it calls the update_post_from_dict() method of the PostAppServices class to update the post with the provided post_id. The updated post object is then serialized using the PostSerializer class. The serialized data of the updated post is returned in an APIResponse object with a status code of 200 and a success message.

        Parameters:
        - request (HttpRequest): The HTTP PATCH request object.
        - pk (int): The primary key of the post to be updated.

        Returns:
        - APIResponse: An APIResponse object containing the serialized data of the updated post and a success message.

        Raises:
        - PostNotFoundException: If the post with the provided post_id does not exist.
        - UnauthorizedPostAccess: If the authenticated user does not have access to the post.
        - Exception: If any other error occurs during the update process.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                post_app_services = PostAppServices()
                post_obj = post_app_services.update_post_from_dict(
                    post_id=pk, user=self.request.user, data=serializer_data.data
                )
                serialized_data = PostSerializer(instance=post_obj)
                return APIResponse(
                    status_code=status.HTTP_200_OK,
                    data=serialized_data.data,
                    message="Post has been updated successfully.",
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

    @action(detail=True, methods=["delete"], name="delete_post")
    def delete_post(self, request, pk):
        """
        Deletes a specific post.

        This method handles the HTTP DELETE request for deleting a specific post. It calls the delete_post() method of the PostAppServices class to delete the post with the provided post_id. If the deletion is successful, it returns an APIResponse object with a status code of 200 and a success message.

        Parameters:
        - request (HttpRequest): The HTTP DELETE request object.
        - pk (int): The primary key of the post to be deleted.

        Returns:
        - APIResponse: An APIResponse object with a status code of 200 and a success message.

        Raises:
        - PostNotFoundException: If the post with the provided post_id does not exist.
        - UnauthorizedPostAccess: If the authenticated user does not have access to the post.
        - Exception: If any other error occurs during the deletion process.

        """
        try:
            post_app_services = PostAppServices()
            post_app_services.delete_post(post_id=pk, user=self.request.user)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="Post has been successfully deleted.",
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

    @action(detail=True, methods=["put"], name="like_unlike_post")
    def like_unlike_post(self, request, pk):
        """
        Updates the like status of a specific post.

        This method handles the HTTP PUT request for liking/unliking a specific post. It calls the like_or_unlike_post() method of the PostLikeAppServices class to update the like status of the post with the provided post_id. The updated post object is then serialized using the PostSerializer class. The serialized data of the updated post is returned in an APIResponse object with a status code of 200 and a success message.

        Parameters:
        - request (HttpRequest): The HTTP PUT request object.
        - pk (int): The primary key of the post to be liked/unliked.

        Returns:
        - APIResponse: An APIResponse object containing the serialized data of the updated post and a success message.

        Raises:
        - PostNotFoundException: If the post with the provided post_id does not exist.
        - UnauthorizedPostAccess: If the authenticated user does not have access to the post.
        - Exception: If any other error occurs during the like/unlike process.

        """
        try:
            post_like_app_services = PostLikeAppServices()
            post_obj, action_message = post_like_app_services.like_or_unlike_post(
                user=self.request.user, post_id=str(pk)
            )
            serialized_data = PostSerializer(instance=post_obj)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message=f"Post {action_message} successfully.",
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

    @action(detail=True, methods=["put"], name="report_post")
    def report_post(self, request, pk):
        """
        Reports a specific post.

        This method handles the HTTP PUT request for reporting a specific post. It calls the post_reporting() method of the PostAppServices class to report the post with the provided post_id. The reported post object is then serialized using the ReportedPostSerializer class. The serialized data of the reported post is returned in an APIResponse object with a status code of 200 and a success message.

        Parameters:
        - request (HttpRequest): The HTTP PUT request object.
        - pk (int): The primary key of the post to be reported.

        Returns:
        - APIResponse: An APIResponse object containing the serialized data of the reported post and a success message.

        Raises:
        - PostNotFoundException: If the post with the provided post_id does not exist.
        - UnauthorizedPostAccess: If the authenticated user does not have access to the post.
        - PostAlreadyReportedException: If the post has already been reported.
        - Exception: If any other error occurs during the reporting process.

        """
        try:
            post_app_services = PostAppServices()
            reported_post_obj = post_app_services.post_reporting(
                post_id=str(pk), user=self.request.user
            )
            serialized_data = ReportedPostSerializer(instance=reported_post_obj)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                data=serialized_data.data,
                message="Post reported successfully.",
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

    @action(detail=False, methods=["get"], name="list_recommend_posts")
    def list_recommend_posts(self, request):
        """
        Retrieves a list of recommended posts.

        This method handles the HTTP GET request for listing recommended posts. It uses the PostRecommendationAppServices class to retrieve a queryset of recommended posts for the authenticated user. The queryset is then serialized using the serializer class obtained from the get_serializer_class() method. The serialized data of the recommended posts is returned in an APIResponse object with a status code of 200 and a success message.

        Parameters:
        - request (HttpRequest): The HTTP GET request object.

        Returns:
        - APIResponse: An APIResponse object containing the serialized data of the recommended posts and a success message.

        Raises:
        - Exception: If an error occurs during the listing process.

        """
        serializer = self.get_serializer_class()
        post_recommendation_app_services = PostRecommendationAppServices()
        queryset = post_recommendation_app_services.list_post_recommendation(
            user=self.request.user
        )
        serialized_data = serializer(queryset, many=True).data
        return APIResponse(
            status_code=status.HTTP_200_OK,
            data=serialized_data,
            message="All recommended posts listed successfully.",
        )


@extend_schema_view(
    create=open_api.post_comment_create_extension,
    list_post_comments=open_api.post_comment_list_extension,
    delete_post_comment=open_api.post_comment_delete_extension,
)
class PostCommentViewSet(viewsets.ViewSet):
    """
    A viewset class that provides CRUD operations for post comments.

    This class extends the ViewSet class from the rest_framework package and provides methods for creating, listing, and deleting post comments. It also includes authentication and permission classes for ensuring that only authenticated users with the necessary permissions can access these operations.

    Attributes:
    - authentication_classes (tuple): A tuple of authentication classes used for authenticating requests.
    - permission_classes (tuple): A tuple of permission classes used for authorizing requests.
    - exception_tuple (tuple): A tuple of exception classes that can be raised during the execution of the methods.

    Methods:
    - get_serializer_class(): Returns the serializer class based on the action being performed.
    - create(request): Creates a new post comment using the provided data and returns the serialized data of the created comment.
    - list_post_comments(request, pk): Retrieves a list of post comments for a specific post and returns the serialized data of the comments.
    - delete_post_comment(request, pk): Deletes a post comment with the provided ID and returns a success message.

    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    exception_tuple = (
        PostNotFoundException,
        PostCommentNotFoundException,
        UnauthorizedPostCommentAccess,
    )

    def get_serializer_class(self):
        """
        Returns the serializer class based on the action being performed.

        This method is used to determine the appropriate serializer class based on the action being performed. If the action is 'create', it returns the 'PostCommentCreateSerializer' class. If the action is 'list_post_comments', it returns the 'PostCommentSerializer' class.

        Returns:
            serializer_class (class): The serializer class based on the action being performed.

        """
        if self.action == "create":
            return PostCommentCreateSerializer
        if self.action == "list_post_comments":
            return PostCommentSerializer

    def create(self, request):
        """
        Creates a new post comment using the provided data and returns the serialized data of the created comment.

        Parameters:
        - request (Request): The HTTP request object.

        Returns:
        - APIResponse: The response object containing the serialized data of the created comment.

        Raises:
        - PostNotFoundException: If the post with the provided ID is not found.
        - PostCommentNotFoundException: If the post comment with the provided ID is not found.
        - UnauthorizedPostCommentAccess: If the user is not authorized to create the post comment.
        - PostAlreadyReportedException: If the post has already been reported.

        """
        serializer = self.get_serializer_class()
        serializer_data = serializer(data=request.data)
        if serializer_data.is_valid():
            try:
                post_id = self.request.query_params.get("post_id")
                if not post_id:
                    return APIResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Post ID is required.",
                        errors={},
                        for_error=True,
                    )
                post_comment_app_services = PostCommentAppServices()
                post_comment_obj = post_comment_app_services.create_post_comment(
                    user=self.request.user,
                    post_id=str(post_id),
                    data=serializer_data.data,
                )
                serialized_data = PostCommentSerializer(instance=post_comment_obj)
                return APIResponse(
                    status_code=status.HTTP_201_CREATED,
                    data=serialized_data.data,
                    message="Comment created successfully.",
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

    @action(detail=True, methods=["get"], name="list_post_comments")
    def list_post_comments(self, request, pk):
        """
        Retrieves a list of post comments for a specific post and returns the serialized data of the comments.

        Parameters:
        - request (Request): The HTTP request object.
        - pk (int): The ID of the post for which the comments are being retrieved.

        Returns:
        - APIResponse: The response object containing the serialized data of the comments.

        """
        serializer = self.get_serializer_class()
        post_comment_app_services = PostCommentAppServices()
        queryset = post_comment_app_services.list_comments_by_post(
            user=self.request.user, post_id=pk
        )
        serialized_data = serializer(queryset, many=True)
        return APIResponse(
            status_code=status.HTTP_200_OK,
            data=serialized_data.data,
            message="All comments listed successfully.",
        )

    @action(detail=True, methods=["delete"], name="delete_post_comment")
    def delete_post_comment(self, request, pk):
        """
        Deletes a post comment with the provided ID.

        Parameters:
        - request (Request): The HTTP request object.
        - pk (int): The ID of the post comment to be deleted.

        Returns:
        - APIResponse: The response object indicating the status of the deletion.

        Raises:
        - PostCommentNotFoundException: If the post comment with the provided ID is not found.
        - UnauthorizedPostCommentAccess: If the user is not authorized to delete the post comment.

        """
        try:
            post_comment_app_services = PostCommentAppServices()
            post_comment_app_services.delete_comment(
                post_comment_id=pk, user=self.request.user
            )
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="Post comment has been successfully deleted.",
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
