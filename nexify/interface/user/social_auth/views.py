from drf_spectacular.utils import extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action

from nexify.application.user.services import UserAppServices
from nexify.infrastructure.custom_response.response_and_error import APIResponse
from nexify.interface.user.social_auth.serializers import GitHubAuthSerializer

from . import open_api


@extend_schema_view(login_with_github=open_api.login_with_github_extension)
class SocialAuthViewSet(viewsets.ViewSet):
    """
    The SocialAuthViewSet class is a viewset that handles social authentication using GitHub.

    Attributes:
    - login_with_github (method): A method that handles the login with GitHub functionality.

    Methods:
    - login_with_github(request): Handles the login with GitHub functionality. It validates the access token provided in the request data and creates a new user if the access token is valid. It returns a response with the user data and a JWT token if the login is successful.

    """

    @action(detail=False, methods=["post"], name="login_with_github")
    def login_with_github(self, request):
        """
        Handles the login with GitHub functionality.

        Parameters:
        - request (HttpRequest): The HTTP request object.

        Returns:
        - APIResponse: The response object containing the user data and a JWT token if the login is successful.

        Raises:
        - Exception: If any other error occurs during the login process.

        Note:
        - This method validates the access token provided in the request data and creates a new user if the access token is valid.
        - If the login is successful, it returns a response with the user data and a JWT token.
        - If the login fails, it returns an appropriate error response.
        """
        serializer_data = GitHubAuthSerializer(data=request.data)
        if serializer_data.is_valid():
            try:
                user_app_services = UserAppServices()
                created, user = user_app_services.create_user_from_github_auth(
                    access_token=serializer_data.data["access_token"]
                )
                if created and user:
                    response_data = user_app_services.get_user_data_with_token(
                        user=user
                    )
                    return APIResponse(
                        data=response_data, message="Login successful via GitHub."
                    )
                return APIResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="Authentication failed! Please try again later.",
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
