from drf_spectacular.utils import extend_schema

from nexify.interface.user.social_auth.serializers import GitHubAuthSerializer

social_auth_tags = ["Social-Auth-Module"]

login_with_github_extension = extend_schema(
    tags=social_auth_tags, request=GitHubAuthSerializer
)
