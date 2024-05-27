from rest_framework import serializers


class GitHubAuthSerializer(serializers.Serializer):
    """
    Serializer for GitHub authentication.

    This serializer is used to validate and deserialize data for GitHub authentication. It expects an access token as input.

    Attributes:
        access_token (CharField): The access token for GitHub authentication.

    """

    access_token = serializers.CharField(required=True)
