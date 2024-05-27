from typing import Any, Dict, Tuple

from django.conf import settings
from django.db import transaction
from django.db.models.query import QuerySet

from nexify.application.file.services import FileAppServices
from nexify.domain.post.models import Post, PostComment, PostLike, ReportedPost
from nexify.domain.post.services import (
    PostCommentServices,
    PostLikeServices,
    PostRecommendationServices,
    PostServices,
    ReportedPostServices,
)
from nexify.domain.user.models import User
from utils.django.exceptions import (
    FileExtensionNotAllowedException,
    PostAlreadyReportedException,
    PostCommentNotFoundException,
    PostNotFoundException,
    UnauthorizedPostAccess,
    UnauthorizedPostCommentAccess,
)


class PostAppServices:
    """
    A class that provides services related to the Post model.

    This class contains methods for listing posts, creating posts, updating posts, deleting posts, and reporting posts. It interacts with the PostServices and ReportedPostServices classes to perform these operations.

    Attributes:
    - post_services (PostServices): An instance of the PostServices class for accessing post-related services.
    - reported_post_services (ReportedPostServices): An instance of the ReportedPostServices class for accessing reported post-related services.
    - file_app_Services (FileAppServices): An instance of the FileAppServices class for accessing file-related services.

    Methods:
    - list_posts() -> QuerySet[Post]: Retrieves a list of active posts in descending order of creation.
    - create_post_from_dict(user: User, data: Dict[str, Any], file_obj=None) -> Post: Creates a new post using the provided user and data.
    - get_post_by_id(post_id: str, user: User) -> Post: Retrieves a post by its ID.
    - check_post_access(post_obj: Post, user: User, action: str) -> None: Checks if the user has access to perform the specified action on the post.
    - update_post_from_dict(post_id: str, user: User, data: Dict[str, Any]) -> Post: Updates a post with the provided ID and data.
    - delete_post(post_id: str, user: User) -> bool: Deletes a post with the provided ID.
    - post_reporting(post_id: str, user: User) -> ReportedPost: Reports a post with the provided ID.

    """

    def __init__(self) -> None:
        self.post_services = PostServices()
        self.reported_post_services = ReportedPostServices()
        self.file_app_Services = FileAppServices()

    def list_posts(self) -> QuerySet[Post]:
        """
        Retrieves a list of active posts in descending order of creation.

        Returns:
            QuerySet[Post]: A queryset of active posts, ordered by creation date in descending order.
        """
        return (
            self.post_services.get_post_repo()
            .filter(is_active=True)
            .order_by("-created_at")
        )

    def create_post_from_dict(
        self,
        user: User,
        data: Dict[str, Any],
        file_obj=None,
    ) -> Post:
        """
        Creates a new post using the provided user and data.

        Parameters:
        - user (User): The user creating the post.
        - data (Dict[str, Any]): A dictionary containing the data for the new post. The dictionary should include the following key:
            - "description" (str): The description of the post.
        - file_obj (Any, optional): The file object to be attached to the post, if any.

        Returns:
        - Post: The newly created post object.

        Raises:
        - FileExtensionNotAllowedException: If the file extension of the attached file is not allowed.
        - Exception: If an error occurs during the creation of the post.
        """

        description = data.get("description", None)

        try:
            with transaction.atomic():
                post_factory_method = self.post_services.get_post_factory()

                if file_obj:
                    file_extension = file_obj.name.split(".")[-1]
                    if file_extension not in settings.ALLOWED_FILE_EXTENSIONS:
                        raise FileExtensionNotAllowedException(
                            item="file-extension-not-allowed-exception",
                            message=f"{file_extension} type file is not allowed. Please try to upload a different type of file.",
                        )

                    file_instance = (
                        self.file_app_Services.create_or_update_file_from_file_obj(
                            file_obj=file_obj, user=user
                        )
                    )
                    link = file_instance.url

                post_obj = post_factory_method.build_entity_with_id(
                    user=user, description=description, link=link if file_obj else None
                )
                post_obj.save()
                return post_obj
        except Exception as e:
            raise e

    def get_post_by_id(self, post_id: str, user: User) -> Post:
        """
        Retrieves a post by its ID.

        Parameters:
        - post_id (str): The ID of the post to retrieve.
        - user (User): The user making the request.

        Returns:
        - Post: The post with the specified ID.

        Raises:
        - PostNotFoundException: If the post with the specified ID does not exist.

        """
        try:
            return self.list_posts().get(id=post_id)
        except Exception as e:
            raise PostNotFoundException(
                item="post-not-found-exception", message="Post not found."
            )

    def check_post_access(self, post_obj: Post, user: User, action: str) -> None:
        """
        Checks if the user has access to perform the specified action on the post.

        Parameters:
        - post_obj (Post): The post object to check access for.
        - user (User): The user making the request.
        - action (str): The action to be performed on the post.

        Raises:
        - UnauthorizedPostAccess: If the user does not have permission to perform the action on the post.

        """
        if str(post_obj.user.id) != str(user.id):
            raise UnauthorizedPostAccess(
                item="unauthorized-post-access",
                message=f"This post can only be {action} by its owner.",
            )

    def update_post_from_dict(
        self, post_id: str, user: User, data: Dict[str, Any]
    ) -> Post:
        """
        Updates a post with the provided ID and data.

        Parameters:
        - post_id (str): The ID of the post to update.
        - user (User): The user making the request.
        - data (Dict[str, Any]): A dictionary containing the data to update the post. The dictionary should include the following key-value pairs:
            - "description" (str): The new description of the post.

        Returns:
        - Post: The updated post.

        Raises:
        - PostNotFoundException: If the post with the specified ID does not exist.
        - UnauthorizedPostAccess: If the user is not the owner of the post and does not have permission to update it.
        - Exception: If an error occurs while updating the post.
        """
        description = data.get("description", None)

        post_obj = self.get_post_by_id(post_id=post_id, user=user)

        if not post_obj:
            raise PostNotFoundException(
                item="post-not-found-exception", message="Post not found."
            )

        self.check_post_access(post_obj=post_obj, user=user, action="modified")

        try:
            with transaction.atomic():
                post_obj.description = description
                post_obj.save()
                return post_obj
        except Exception as e:
            raise e

    def delete_post(self, post_id: str, user: User) -> bool:
        """
        Deletes a post with the provided ID.

        Parameters:
        - post_id (str): The ID of the post to delete.
        - user (User): The user making the request.

        Returns:
        - bool: True if the post is successfully deleted.

        Raises:
        - PostNotFoundException: If the post with the specified ID does not exist.
        - UnauthorizedPostAccess: If the user is not the owner of the post and does not have permission to delete it.
        - Exception: If an error occurs while deleting the post.

        """
        post_obj = self.list_posts().filter(id=post_id).first()

        if not post_obj:
            raise PostNotFoundException(
                item="post-not-found-exception", message="Post not found."
            )

        self.check_post_access(post_obj=post_obj, user=user, action="deleted")

        try:
            with transaction.atomic():
                post_obj.delete()
                return True
        except Exception as e:
            raise e

    def post_reporting(self, post_id: str, user: User) -> ReportedPost:
        """
        Reports a post with the provided ID.

        Parameters:
        - post_id (str): The ID of the post to report.
        - user (User): The user making the report.

        Returns:
        - ReportedPost: The reported post object.

        Raises:
        - PostNotFoundException: If the post with the specified ID does not exist.
        - PostAlreadyReportedException: If the user has already reported the post.
        - Exception: If an error occurs while reporting the post.

        """
        post_obj = self.list_posts().filter(id=post_id).first()

        if not post_obj:
            raise PostNotFoundException(
                item="post-not-found-exception", message="Post not found."
            )

        exist_reported_post_obj = (
            self.reported_post_services.get_reported_post_repo()
            .filter(post=post_id, user=str(user.id))
            .first()
        )
        if exist_reported_post_obj:
            raise PostAlreadyReportedException(
                item="post-already-reported-exception",
                message="You have already reported this post.",
            )

        try:
            with transaction.atomic():
                reported_post_factory_method = (
                    self.reported_post_services.get_reported_post_factory()
                )
                reported_post_obj = reported_post_factory_method.build_entity_with_id(
                    post=post_obj, user=user
                )
                reported_post_obj.save()

                # Increase the number of post report count.
                post_obj.is_reported = True
                post_obj.report_count += 1
                post_obj.save()

                return reported_post_obj
        except Exception as e:
            raise e


class PostCommentAppServices:
    """
    A class that provides services related to post comments in the PostApp.

    This class encapsulates various methods for creating, retrieving, and deleting post comments.

    Attributes:
    - post_comment_services (PostCommentServices): An instance of the PostCommentServices class for accessing post comment-related services.
    - post_app_services (PostAppServices): An instance of the PostAppServices class for accessing post-related services.

    Methods:
    - list_comments(): Retrieves a list of active post comments in descending order of creation.
    - create_post_comment(user: User, post_id: str, data: Dict[str, Any]) -> PostComment: Creates a new post comment using the provided user, post ID, and data.
    - list_comments_by_post(user: User, post_id: str) -> QuerySet[PostComment]: Retrieves a list of active post comments for a specific post in descending order of creation.
    - delete_comment(post_comment_id: str, user: User) -> bool: Deletes a post comment with the provided ID.

    """

    def __init__(self) -> None:
        self.post_comment_services = PostCommentServices()
        self.post_app_services = PostAppServices()

    def list_comments(self) -> QuerySet[PostComment]:
        """
        Retrieves a list of active post comments in descending order of creation.

        Returns:
            QuerySet[PostComment]: A queryset of active post comments.

        """
        return (
            self.post_comment_services.get_post_comment_repo()
            .filter(is_active=True)
            .order_by("-created_at")
        )

    def create_post_comment(
        self, user: User, post_id: str, data: Dict[str, Any]
    ) -> PostComment:
        """
        Creates a new post comment using the provided user, post ID, and data.

        Parameters:
        - user (User): The user who is creating the comment.
        - post_id (str): The ID of the post on which the comment is being made.
        - data (Dict[str, Any]): Additional data for the comment, such as the description.

        Returns:
        - PostComment: The newly created post comment.

        Raises:
        - Exception: If there is an error while creating the comment.

        """
        description = data.get("description", None)

        post_obj = self.post_app_services.get_post_by_id(post_id=post_id, user=user)

        try:
            with transaction.atomic():
                post_comment_factory_method = (
                    self.post_comment_services.get_post_comment_factory()
                )
                post_comment_obj = post_comment_factory_method.build_entity_with_id(
                    post=post_obj, user=user, description=description
                )
                post_comment_obj.save()

                # Updating the number of comments count.
                post_obj.comments_count += 1
                post_obj.save()

                return post_comment_obj
        except Exception as e:
            raise e

    def list_comments_by_post(self, user: User, post_id: str) -> QuerySet[PostComment]:
        """
        Retrieves a list of active post comments for a specific post in descending order of creation.

        Parameters:
        - user (User): The user who is requesting the comments.
        - post_id (str): The ID of the post for which the comments are being retrieved.

        Returns:
        - QuerySet[PostComment]: A queryset of active post comments for the specified post.

        """
        return (
            self.post_comment_services.get_post_comment_repo()
            .filter(post=post_id, is_active=True)
            .order_by("-created_at")
        )

    def delete_comment(self, post_comment_id: str, user: User) -> bool:
        """
        Deletes a post comment with the provided ID.

        Parameters:
        - post_comment_id (str): The ID of the post comment to be deleted.
        - user (User): The user who is requesting the deletion.

        Returns:
        - bool: True if the post comment is successfully deleted, False otherwise.

        Raises:
        - PostCommentNotFoundException: If the post comment with the provided ID is not found.
        - UnauthorizedPostCommentAccess: If the user is not authorized to delete the post comment.

        """
        post_comment_obj = self.list_comments().filter(id=post_comment_id).first()

        if not post_comment_obj:
            raise PostCommentNotFoundException(
                item="post-comment-not-found-exception",
                message="Post comment not found.",
            )

        if str(post_comment_obj.user.id) != str(user.id):
            raise UnauthorizedPostCommentAccess(
                item="unauthorized-post-comment-access",
                message="This comment can only be deleted by its owner.",
            )

        try:
            with transaction.atomic():
                # Updating the number of comments count.
                post_obj = self.post_app_services.get_post_by_id(
                    post_id=str(post_comment_obj.post.id), user=user
                )
                post_obj.comments_count -= 1
                post_obj.save()

                post_comment_obj.delete()
                return True
        except Exception as e:
            return e


class PostLikeAppServices:
    """
    A class that provides services related to liking and unliking posts in the PostApp.

    This class encapsulates methods for liking and unliking posts, as well as updating the like count of posts.

    Attributes:
    - post_like_services (PostLikeServices): An instance of the PostLikeServices class for accessing post like-related services.
    - post_app_services (PostAppServices): An instance of the PostAppServices class for accessing post-related services.

    Methods:
    - list_post_likes() -> QuerySet[PostLike]: Retrieves a list of active post likes in descending order of creation.
    - like_or_unlike_post(user: User, post_id: str) -> Tuple[Post, str]: Likes or unlikes a post with the provided user and post ID.

    """

    def __init__(self) -> None:
        self.post_like_services = PostLikeServices()
        self.post_app_services = PostAppServices()

    def list_post_likes(self) -> QuerySet[PostLike]:
        """
        Returns a QuerySet of all active PostLikes, ordered by their creation date in descending order.

        Returns:
            QuerySet[PostLike]: A QuerySet containing all active PostLikes.

        """
        return (
            self.post_like_services.get_post_like_repo()
            .filter(is_active=True)
            .order_by("-created_at")
        )

    def like_or_unlike_post(self, user: User, post_id: str) -> Tuple[Post, str]:
        """
        Likes or unlikes a post with the provided user and post ID.

        Parameters:
        - user (User): The user who is liking or unliking the post.
        - post_id (str): The ID of the post to be liked or unliked.

        Returns:
        Tuple[Post, str]: A tuple containing the updated post object and an action message indicating whether the post was liked or unliked.

        Raises:
        - PostNotFoundException: If the post with the provided ID does not exist.
        - UnauthorizedPostAccess: If the user does not have permission to like or unlike the post.
        - PostCommentNotFoundException: If the post comment with the provided ID does not exist.
        - UnauthorizedPostCommentAccess: If the user does not have permission to like or unlike the post comment.
        - PostAlreadyReportedException: If the post has already been reported.

        """
        post_obj = self.post_app_services.get_post_by_id(post_id=post_id, user=user)

        exist_post_like_obj = (
            self.post_like_services.get_post_like_repo()
            .filter(post=post_id, user=str(user.id))
            .first()
        )

        try:
            with transaction.atomic():
                if exist_post_like_obj:
                    # Decrease the number of likes.
                    post_obj.likes_count -= 1

                    exist_post_like_obj.delete()

                    action_message = "unliked"

                else:
                    post_like_factory_method = (
                        self.post_like_services.get_post_like_factory()
                    )
                    post_like_obj = post_like_factory_method.build_entity_with_id(
                        post=post_obj, user=user
                    )
                    post_like_obj.save()

                    # Increase the number of likes.
                    post_obj.likes_count += 1

                    action_message = "liked"

                post_obj.save()

                return post_obj, action_message
        except Exception as e:
            raise e


class PostRecommendationAppServices:
    """
    A class representing services for managing Post recommendations for users.

    This class provides methods for retrieving a list of recommended posts for a specified user.

    Attributes:
    - post_recommendation_services (PostRecommendationServices): An instance of PostRecommendationServices for managing PostRecommendation instances.

    Methods:
    - list_post_recommendation(user: User) -> QuerySet[Post]: Retrieves a list of recommended posts for the specified user.

    """

    def __init__(self) -> None:
        self.post_recommendation_services = PostRecommendationServices()

    def list_post_recommendation(self, user: User) -> QuerySet[Post]:
        """
        Retrieves a list of recommended posts for the specified user.

        Parameters:
        - user (User): The user for whom to retrieve the recommended posts.

        Returns:
        - QuerySet[Post]: A queryset of recommended posts for the specified user.

        """
        return (
            self.post_recommendation_services.get_post_recommendation_repo()
            .filter(user=user)
            .first()
            .recommend_posts.all()
        )
