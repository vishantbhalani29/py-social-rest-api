from rest_framework import serializers

from nexify.domain.post.models import Post, PostComment, PostLike, ReportedPost
from nexify.interface.user.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    """
    A serializer class for the Post model.

    This serializer is used to convert Post model instances into JSON format and vice versa. It defines the fields that should be included in the serialized representation of a Post object.

    Attributes:
    - user (UserSerializer): The serializer for the User model, used to represent the User who created the Post.

    Meta:
    - model (Post): The model class that the serializer is based on, set to Post.
    - exclude (list): The list of fields to exclude from the serialized representation, set to ["created_at", "modified_at"].
    """

    user = UserSerializer()

    class Meta:
        model = Post
        exclude = ["created_at", "modified_at"]


class PostCreateSerializer(serializers.ModelSerializer):
    """
    A serializer class for creating a Post.

    This serializer is used to validate and deserialize data for creating a new Post instance. It is designed to work with the Post model and has a single field, "description", which represents the description of the Post.

    Attributes:
    - model (Model): The model class that the serializer is based on, set to Post.
    - fields (list): The list of fields to include in the serializer, set to ["description"].
    """

    class Meta:
        model = Post
        fields = ["description"]


class PostUpdateSerializer(PostCreateSerializer):
    """
    A serializer class for updating a Post.

    This serializer is used to validate and deserialize data for updating an existing Post instance. It is designed to work with the Post model and inherits from the PostCreateSerializer class. It does not add any additional fields or attributes.

    Attributes:
    - model (Model): The model class that the serializer is based on, set to Post.
    - fields (list): The list of fields to include in the serializer, set to ["description"].
    """

    pass


class PostCommentSerializer(serializers.ModelSerializer):
    """
    A serializer class for the PostComment model.

    This serializer is used to convert PostComment model instances into JSON format and vice versa. It defines the fields that should be included in the serialized representation of a PostComment object.

    Attributes:
    - user (UserSerializer): A serializer for the User model, used to represent the user who made the comment.

    Meta:
    - model (PostComment): The model class that this serializer is associated with.
    - exclude (list): A list of fields to be excluded from the serialized representation of a PostComment object.

    """

    user = UserSerializer()

    class Meta:
        model = PostComment
        exclude = ["created_at", "modified_at"]


class PostCommentCreateSerializer(serializers.ModelSerializer):
    """
    A serializer class for creating a new PostComment instance.

    This serializer is used to validate and deserialize the data received for creating a new PostComment instance. It specifies the fields that are allowed to be included in the serialized representation of the PostComment model.

    Attributes:
    - model (Model): The model class that the serializer is based on, set to PostComment.
    - fields (list): The list of fields that are included in the serialized representation, set to ["description"].

    """

    class Meta:
        model = PostComment
        fields = ["description"]


class PostLikeSerializer(serializers.ModelSerializer):
    """
    Serializer class for the PostLike model.

    This serializer is used to convert PostLike model instances into JSON format and vice versa. It defines the fields that should be included in the serialized representation of a PostLike object.

    Attributes:
    - user (UserSerializer): Serializer for the User model, used to represent the user who liked the post.

    Meta:
    - model (PostLike): The model class that this serializer is associated with.
    - exclude (list): List of fields to exclude from the serialized representation.

    """

    user = UserSerializer()

    class Meta:
        model = PostLike
        exclude = ["created_at", "modified_at"]


class ReportedPostSerializer(serializers.ModelSerializer):
    """
    A serializer class for the ReportedPost model.

    This serializer is used to convert ReportedPost model instances into JSON format and vice versa. It defines the fields that should be included in the serialized representation of a ReportedPost object.

    Attributes:
    - user (UserSerializer): The serializer for the User model, used to represent the User who reported the Post.
    - post (PostSerializer): The serializer for the Post model, used to represent the Post that has been reported.

    Meta:
    - model (ReportedPost): The model class that the serializer is based on, set to ReportedPost.
    - exclude (list): The list of fields to exclude from the serialized representation, set to ["created_at", "modified_at"].
    """

    user = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = ReportedPost
        exclude = ["created_at", "modified_at"]
