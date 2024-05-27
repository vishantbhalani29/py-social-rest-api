"""
This module defines the models for the Post, PostComment, PostLike, and ReportedPost entities in the project.

Usage:
- Use PostID, PostCommentID, PostLikeID, and ReportedPostID to create unique identifiers for Post, PostComment, PostLike, and ReportedPost instances.
- Use Post, PostComment, PostLike, ReportedPost, and PostRecommendation to create, retrieve, update, and delete corresponding objects in the database.
- Use PostFactory, PostCommentFactory, PostLikeFactory, and ReportedPostFactory to create instances of Post, PostComment, PostLike, and ReportedPost entities with or without specific IDs.

"""

import uuid
from dataclasses import dataclass

from django.db import models

from nexify.domain.file.models import File
from nexify.domain.user.models import User
from utils.django import custom_models


@dataclass(frozen=True)
class PostID:
    """
    A class representing the ID of a Post.

    Attributes:
        value (uuid.UUID): The unique identifier value of the Post ID.

    """

    value: uuid.UUID


@dataclass(frozen=True)
class PostCommentID:
    """
    A class representing the ID of a Post Comment.

    Attributes:
        value (uuid.UUID): The unique identifier value of the Post Comment ID.

    """

    value: uuid.UUID


@dataclass(frozen=True)
class PostLikeID:
    """
    A class representing the ID of a Post Like.

    Attributes:
        value (uuid.UUID): The unique identifier value of the Post Like ID.

    """

    value: uuid.UUID


@dataclass(frozen=True)
class ReportedPostID:
    """
    A class representing the ID of a Reported Post.

    Attributes:
        value (uuid.UUID): The unique identifier value of the Reported Post ID.

    """

    value: uuid.UUID


# --------------------------------------------------
# Post Model
# --------------------------------------------------


class Post(custom_models.ActivityTracking):
    """
    A class representing a Post.

    This class extends the ActivityTracking class from the custom_models module to track the activity state of Post instances.

    Attributes:
    - id (UUIDField): The unique identifier for the Post.
    - user (ForeignKey): The User who created the Post.
    - description (TextField): The description of the Post.
    - link (CharField): The link associated with the Post.
    - likes_count (PositiveIntegerField): The number of likes the Post has received.
    - comments_count (PositiveIntegerField): The number of comments the Post has received.
    - is_reported (BooleanField): Flag to indicate whether the Post has been reported or not.
    - report_count (PositiveIntegerField): The number of times the post has been reported.

    Methods:
    - get_file: Returns the File object associated with the post's link.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "Post".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "Posts".
    - db_table (str): The name of the database table for this model, set to "post".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=300, blank=True, null=True)
    link = models.CharField(null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)

    def get_file(self):
        return File.objects.filter(url=self.link, is_active=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        db_table = "post"


class PostFactory:
    """
    A factory class for creating instances of the Post class.

    This class provides static methods for building Post entities with or without an ID.

    Methods:
    - build_entity(id: PostID, user: User, description: str, link: str) -> Post:
        Builds and returns a Post entity with the given ID, user, description, and link.

    - build_entity_with_id(user: User, description: str, link: str) -> Post:
        Builds and returns a Post entity with a newly generated ID, the given user, description, and link.

    """

    @staticmethod
    def build_entity(
        id: PostID,
        user: User,
        description: str,
        link: str = None,
    ) -> Post:
        return Post(
            id=id.value,
            user=user,
            description=description,
            link=link,
        )

    @classmethod
    def build_entity_with_id(
        cls,
        user: User,
        description: str,
        link: str = None,
    ) -> Post:
        entity_id = PostID(uuid.uuid4())
        return cls.build_entity(
            id=entity_id,
            user=user,
            description=description,
            link=link,
        )


# --------------------------------------------------
# PostComment Model
# --------------------------------------------------


class PostComment(custom_models.ActivityTracking):
    """
    A class representing a comment on a post.

    This class extends the ActivityTracking class from the custom_models module to track the activity state of PostComment instances.

    Attributes:
    - id (UUIDField): The unique identifier for the comment.
    - post (ForeignKey): The post on which the comment is made.
    - user (ForeignKey): The user who made the comment.
    - description (TextField): The content of the comment.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "PostComment".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "PostComments".
    - db_table (str): The name of the database table for this model, set to "post_comment".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=100)

    class Meta:
        verbose_name = "PostComment"
        verbose_name_plural = "PostComments"
        db_table = "post_comment"


class PostCommentFactory:
    """
    A factory class for creating instances of the PostComment class.

    This class provides two methods for creating PostComment entities with or without an ID.

    Methods:
    - build_entity: Creates a PostComment instance with a specified ID, post, user, and description.
    - build_entity_with_id: Creates a PostComment instance with a randomly generated ID, and specified post, user, and description.

    """

    @staticmethod
    def build_entity(
        id: PostCommentID,
        post: Post,
        user: User,
        description: str,
    ) -> PostComment:
        return PostComment(
            id=id.value,
            post=post,
            user=user,
            description=description,
        )

    @classmethod
    def build_entity_with_id(
        cls,
        post: Post,
        user: User,
        description: str,
    ) -> PostComment:
        entity_id = PostCommentID(uuid.uuid4())
        return cls.build_entity(
            id=entity_id,
            post=post,
            user=user,
            description=description,
        )


# --------------------------------------------------
# PostLike Model
# --------------------------------------------------


class PostLike(custom_models.ActivityTracking):
    """
    A class representing a like on a Post.

    This class extends the ActivityTracking class from the custom_models module to track the activity state of PostLike instances.

    Attributes:
    - id (UUIDField): The unique identifier for the Post Like.
    - post (ForeignKey): The Post that was liked.
    - user (ForeignKey): The User who liked the Post.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "PostLike".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "PostLikes".
    - db_table (str): The name of the database table for this model, set to "post_like".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "PostLike"
        verbose_name_plural = "PostLikes"
        db_table = "post_like"


class PostLikeFactory:
    """
    A factory class for creating instances of the PostLike model.

    This class provides methods for building PostLike entities with or without an ID.

    Methods:
    - build_entity: Builds a PostLike entity with the given ID, post, and user.
    - build_entity_with_id: Builds a PostLike entity with a new ID, using the given post and user.

    """

    @staticmethod
    def build_entity(
        id: PostLikeID,
        post: Post,
        user: User,
    ) -> PostLike:
        return PostLike(
            id=id.value,
            post=post,
            user=user,
        )

    @classmethod
    def build_entity_with_id(
        cls,
        post: Post,
        user: User,
    ) -> PostLike:
        entity_id = PostLikeID(uuid.uuid4())
        return cls.build_entity(
            id=entity_id,
            post=post,
            user=user,
        )


# --------------------------------------------------
# ReportedPost Model
# --------------------------------------------------


class ReportedPost(custom_models.ActivityTracking):
    """
    A class representing a ReportedPost.

    This class extends the ActivityTracking class from the custom_models module to track the activity state of ReportedPost instances.

    Attributes:
    - id (UUIDField): The unique identifier for the ReportedPost.
    - post (ForeignKey): The Post that has been reported.
    - user (ForeignKey): The User who reported the Post.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "ReportedPost".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "ReportedPosts".
    - db_table (str): The name of the database table for this model, set to "reported_post".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "ReportedPost"
        verbose_name_plural = "ReportedPosts"
        db_table = "reported_post"


class ReportedPostFactory:
    """
    A factory class for creating ReportedPost instances.

    This class provides methods for building ReportedPost entities with different parameters.

    Methods:
    - build_entity: Builds a ReportedPost entity with the given ID, post, and user.
    - build_entity_with_id: Builds a ReportedPost entity with a new ID and the given post and user.

    """

    @staticmethod
    def build_entity(
        id: ReportedPostID,
        post: Post,
        user: User,
    ) -> ReportedPost:
        return ReportedPost(
            id=id.value,
            post=post,
            user=user,
        )

    @classmethod
    def build_entity_with_id(
        cls,
        post: Post,
        user: User,
    ) -> ReportedPost:
        entity_id = ReportedPostID(uuid.uuid4())
        return cls.build_entity(
            id=entity_id,
            post=post,
            user=user,
        )


# --------------------------------------------------
# PostRecommendation Model
# --------------------------------------------------


class PostRecommendation(custom_models.ActivityTracking):
    """
    A class representing a Post Recommendation.

    This class extends the ActivityTracking class from the custom_models module to track the activity state of PostRecommendation instances.

    Attributes:
    - id (UUIDField): The unique identifier for the PostRecommendation.
    - user (ForeignKey): The User who made the recommendation.
    - recommend_posts (ManyToManyField): The recommended posts associated with the PostRecommendation.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "PostRecommendation".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "PostRecommendations".
    - db_table (str): The name of the database table for this model, set to "post_recommendation".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommend_posts = models.ManyToManyField(Post, blank=True)

    class Meta:
        verbose_name = "PostRecommendation"
        verbose_name_plural = "PostRecommendations"
        db_table = "post_recommendation"
