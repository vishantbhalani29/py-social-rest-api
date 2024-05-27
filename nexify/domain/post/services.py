from typing import Type

from django.db.models.manager import BaseManager

from .models import (
    Post,
    PostComment,
    PostCommentFactory,
    PostFactory,
    PostLike,
    PostLikeFactory,
    PostRecommendation,
    ReportedPost,
    ReportedPostFactory,
)


class PostServices:
    """
    A class that provides services related to the Post model.

    This class contains methods for retrieving the PostFactory and PostRepo instances, as well as retrieving a Post entity by its ID.

    Methods:
    - get_post_factory() -> Type[PostFactory]:
        Returns the PostFactory class.

    - get_post_repo() -> BaseManager[Post]:
        Returns the PostRepo instance.

    - get_post_by_id(id: str) -> Post:
        Retrieves a Post entity by its ID.

    """

    @staticmethod
    def get_post_factory() -> Type[PostFactory]:
        """
        Returns the PostFactory class.

        Returns:
            Type[PostFactory]: The PostFactory class.
        """
        return PostFactory

    @staticmethod
    def get_post_repo() -> BaseManager[Post]:
        """
        Returns the PostRepo instance.

        Returns:
            BaseManager[Post]: The PostRepo instance.
        """
        return Post.objects

    def get_post_by_id(self, id: str) -> Post:
        """
        Retrieves a Post entity by its ID.

        Parameters:
        - id (str): The ID of the Post entity to retrieve.

        Returns:
        - Post: The Post entity with the specified ID.
        """
        return Post.objects.get(id=id)


class PostCommentServices:
    """
    A class that provides services related to PostComment entities.

    This class provides methods for accessing the PostCommentFactory and PostComment repository, as well as retrieving PostComment instances by their ID.

    Attributes:
    - None

    Methods:
    - get_post_comment_factory: Returns the PostCommentFactory class.
    - get_post_comment_repo: Returns the PostComment repository.
    - get_post_comment_by_id: Retrieves a PostComment instance by its ID.

    """

    @staticmethod
    def get_post_comment_factory() -> Type[PostCommentFactory]:
        """
        Returns the PostCommentFactory class.

        Returns:
            Type[PostCommentFactory]: The PostCommentFactory class.
        """
        return PostCommentFactory

    @staticmethod
    def get_post_comment_repo() -> BaseManager[PostComment]:
        """
        Returns the PostComment repository.

        This method returns the repository for accessing PostComment instances.

        Returns:
            BaseManager[PostComment]: The PostComment repository.
        """
        return PostComment.objects

    def get_post_comment_by_id(self, id: str) -> PostComment:
        """
        Retrieves a PostComment instance by its ID.

        This method takes an ID as input and returns the corresponding PostComment instance from the database.

        Parameters:
        - id (str): The ID of the PostComment instance to retrieve.

        Returns:
        - PostComment: The PostComment instance with the specified ID.

        """
        return PostComment.objects.get(id=id)


class PostLikeServices:
    """
    A class that provides services related to Post Likes.

    This class provides methods for accessing and manipulating Post Like entities.

    Attributes:
    - None

    Methods:
    - get_post_like_factory: Returns the factory class for creating instances of the PostLike model.
    - get_post_like_repo: Returns the repository for accessing Post Like entities.
    - get_post_like_by_id: Retrieves a Post Like entity by its ID.

    """

    @staticmethod
    def get_post_like_factory() -> Type[PostLikeFactory]:
        """
        Returns the factory class for creating instances of the PostLike model.

        Returns:
            Type[PostLikeFactory]: The factory class for creating instances of the PostLike model.
        """
        return PostLikeFactory

    @staticmethod
    def get_post_like_repo() -> BaseManager[PostLike]:
        """
        Returns the repository for accessing Post Like entities.

        Returns:
            BaseManager[PostLike]: The repository for accessing Post Like entities.
        """
        return PostLike.objects

    def get_post_like_by_id(self, id: str) -> PostLike:
        """
        Retrieves a Post Like entity by its ID.

        Parameters:
        - id (str): The ID of the Post Like entity to retrieve.

        Returns:
            PostLike: The Post Like entity with the specified ID.
        """
        return PostLike.objects.get(id=id)


class ReportedPostServices:
    """
    A class representing the services for ReportedPost.

    This class provides methods for interacting with ReportedPost entities, including creating instances, retrieving instances by ID, and accessing the ReportedPost repository.

    Attributes:
    - None

    Methods:
    - get_reported_post_factory: Returns the factory class for creating ReportedPost instances.
    - get_reported_post_repo: Returns the repository for accessing ReportedPost instances.
    - get_reported_post_by_id: Retrieves a ReportedPost instance by its ID.

    """

    @staticmethod
    def get_reported_post_factory() -> Type[ReportedPostFactory]:
        """
        Returns the factory class for creating ReportedPost instances.

        Returns:
            Type[ReportedPostFactory]: The factory class for creating ReportedPost instances.
        """
        return ReportedPostFactory

    @staticmethod
    def get_reported_post_repo() -> BaseManager[ReportedPost]:
        """
        Returns the repository for accessing ReportedPost instances.

        Returns:
            BaseManager[ReportedPost]: The repository for accessing ReportedPost instances.
        """
        return ReportedPost.objects

    def get_reported_post_by_id(self, id: str) -> ReportedPost:
        """
        Retrieves a ReportedPost instance by its ID.

        Parameters:
        - id (str): The ID of the ReportedPost instance to retrieve.

        Returns:
        - ReportedPost: The Retrieved ReportedPost instance.

        """
        return ReportedPost.objects.get(id=id)


class PostRecommendationServices:
    """
    A class representing services for managing PostRecommendation instances.

    This class provides methods for retrieving, creating, updating, and deleting PostRecommendation instances.

    Methods:
    - get_post_recommendation_repo: Returns the repository for accessing PostRecommendation instances.

    """

    @staticmethod
    def get_post_recommendation_repo() -> BaseManager[PostRecommendation]:
        """
        Returns the repository for accessing PostRecommendation instances.

        Returns:
            BaseManager[PostRecommendation]: The repository for accessing PostRecommendation instances.
        """
        return PostRecommendation.objects
