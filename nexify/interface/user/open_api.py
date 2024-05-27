from drf_spectacular.utils import extend_schema

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
)

auth_tags = ["Auth-Module"]
user_tags = ["User-Module"]
user_follow_tags = ["User-Follow-Module"]

user_sign_up_extension = extend_schema(
    tags=auth_tags,
    request=UserSignUpSerializer,
    responses={200: UserSerializer},
)

user_login_extension = extend_schema(
    tags=auth_tags,
    request=UserLoginSerializer,
    responses={201: UserSerializer},
)

user_list_extension = extend_schema(
    tags=user_tags,
    responses={200: UserSerializer},
)

user_retrieve_extension = extend_schema(
    tags=user_tags,
    responses={200: UserSerializer},
)

user_update_extension = extend_schema(
    tags=user_tags,
    responses={200: UserSerializer},
)

user_delete_extension = extend_schema(
    tags=user_tags,
    responses={200: {}},
)

user_follow_unfollow_extension = extend_schema(
    tags=user_follow_tags,
    responses={200: UserSerializer},
)

accept_follow_request_extension = extend_schema(
    tags=user_follow_tags,
    responses={200: UserFollowSerializer},
)

user_follow_requests_extension = extend_schema(
    tags=user_follow_tags,
    responses={200: UserFollowRequestsSerializer},
)

user_followers_extension = extend_schema(
    tags=user_follow_tags,
    responses={200: UserFollowersSerializer},
)
user_following_extension = extend_schema(
    tags=user_follow_tags,
    responses={200: UserFollowingSerializer},
)

delete_follow_request_extension = extend_schema(
    tags=user_follow_tags,
    responses={200: {}},
)

user_forgot_password_extension = extend_schema(
    tags=auth_tags,
    request=ForgotPasswordSerializer,
    responses={200: {}},
)

user_reset_password_extension = extend_schema(
    tags=auth_tags,
    request=ResetPasswordSerializer,
    responses={200: {}},
)
