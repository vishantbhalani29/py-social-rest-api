from rest_framework import serializers

from nexify.domain.user.models import User, UserFollow


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for the User model.

    This serializer is used to convert User model instances into JSON format and vice versa. It specifies the fields that should be included in the serialized representation of a User instance.

    Attributes:
        model (class): The User model class that this serializer is associated with.
        fields (list): The list of fields to be included in the serialized representation of a User instance.

    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "is_active",
            "created_at",
        ]


class UserSignUpSerializer(serializers.Serializer):
    """
    Serializer class for user sign up.

    This serializer is used to validate and serialize user sign up data. It specifies the fields that should be included in the serialized representation of a user sign up.

    Attributes:
        email (CharField): The email field for the user sign up.
        first_name (CharField): The first name field for the user sign up.
        last_name (CharField): The last name field for the user sign up.
        password (CharField): The password field for the user sign up.

    """

    email = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=60, required=True)
    last_name = serializers.CharField(max_length=60, required=True)
    password = serializers.CharField(max_length=60, required=True)


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer class for user login.

    This serializer is used to validate and serialize user login data. It specifies the fields that should be included in the serialized representation of a user login.

    Attributes:
        email (CharField): The email field for the user login.
        password (CharField): The password field for the user login.

    """

    email = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True)


class UserUpdateSerializer(serializers.Serializer):
    """
    Serializer class for updating user information.

    This serializer is used to validate and serialize user update data. It specifies the fields that should be included in the serialized representation of a user update.

    Attributes:
        email (EmailField): The email field for the user update.
        first_name (CharField): The first name field for the user update.
        last_name (CharField): The last name field for the user update.

    Methods:
        validate(data): Validates the input data and checks for unexpected fields.

    """

    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def validate(self, data):
        request_keys = set(self.initial_data.keys())
        valid_keys = set(self.fields.keys())
        if not request_keys.issubset(valid_keys):
            extra_keys = request_keys - valid_keys
            raise serializers.ValidationError(
                f"Unexpected fields provided: {', '.join(extra_keys)}"
            )
        return data


class UserFollowSerializer(serializers.ModelSerializer):
    """
    Serializer class for the UserFollow model.

    This serializer is used to convert UserFollow model instances into JSON format and vice versa. It specifies the fields that should be included in the serialized representation of a UserFollow instance.

    Attributes:
        follower (UserSerializer): Serializer for the follower field, which represents the user who is following another user.
        following (UserSerializer): Serializer for the following field, which represents the user who is being followed by another user.

    Meta:
        model (class): The UserFollow model class that this serializer is associated with.
        exclude (list): The list of fields to be excluded from the serialized representation of a UserFollow instance.

    """

    follower = UserSerializer()
    following = UserSerializer()

    class Meta:
        model = UserFollow
        exclude = ["created_at", "modified_at", "is_active"]


class UserFollowRequestsSerializer(UserFollowSerializer):
    """
    Serializer class for the UserFollowRequestsSerializer model.

    This serializer is used to convert UserFollowRequestsSerializer model instances into JSON format and vice versa. It specifies the fields that should be included in the serialized representation of a UserFollowRequestsSerializer instance.

    Attributes:
        id (UUIDField): The unique identifier for the UserFollowRequestsSerializer instance.
        follower (UserSerializer): Serializer for the follower field, which represents the user who is following another user.
        is_accepted (BooleanField): Flag to indicate whether the follow request is accepted or not.

    Meta:
        model (class): The UserFollowRequestsSerializer model class that this serializer is associated with.
        fields (list): The list of fields to be included in the serialized representation of a UserFollowRequestsSerializer instance.

    """

    class Meta:
        model = UserFollow
        fields = ["id", "follower", "is_accepted"]


class UserFollowersSerializer(UserFollowRequestsSerializer):
    """
    Serializer class for the UserFollowersSerializer model.

    This serializer is used to convert UserFollowersSerializer model instances into JSON format and vice versa. It inherits from the UserFollowRequestsSerializer class and specifies the fields that should be included in the serialized representation of a UserFollowersSerializer instance.

    Attributes:
        id (UUIDField): The unique identifier for the UserFollowersSerializer instance.
        follower (UserSerializer): Serializer for the follower field, which represents the user who is following another user.
        is_accepted (BooleanField): Flag to indicate whether the follow request is accepted or not.

    Meta:
        model (class): The UserFollowersSerializer model class that this serializer is associated with.
        fields (list): The list of fields to be included in the serialized representation of a UserFollowersSerializer instance.

    """

    pass


class UserFollowingSerializer(UserFollowSerializer):
    """
    Serializer class for the UserFollowingSerializer model.

    This serializer is used to convert UserFollowingSerializer model instances into JSON format and vice versa. It specifies the fields that should be included in the serialized representation of a UserFollowingSerializer instance.

    Attributes:
        id (UUIDField): The unique identifier for the UserFollowingSerializer instance.
        following (UserSerializer): Serializer for the following field, which represents the user who is being followed by another user.
        is_accepted (BooleanField): Flag to indicate whether the follow request is accepted or not.
            Defaults to False.

    Meta:
        model (class): The UserFollowingSerializer model class that this serializer is associated with.
        fields (list): The list of fields to be included in the serialized representation of a UserFollowingSerializer instance.

    """

    class Meta:
        model = UserFollow
        fields = ["id", "following", "is_accepted"]


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer class for the ForgotPasswordSerializer model.

    This serializer is used to validate and serialize the email field for the forgot password functionality.

    Attributes:
        email (CharField): The email field for the forgot password functionality.

    """

    email = serializers.CharField(max_length=150, required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer class for resetting user password.

    This serializer is used to validate and serialize the token and new password fields for the reset password functionality.

    Attributes:
        token (CharField): The token field for the reset password functionality.
        new_password (CharField): The new password field for the reset password functionality.

    """

    token = serializers.CharField(max_length=350, required=True)
    new_password = serializers.CharField(max_length=20, required=True)
