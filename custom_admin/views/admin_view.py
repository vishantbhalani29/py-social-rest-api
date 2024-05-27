from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View


class MyLoginView(LoginView):
    """
    A custom login view that extends the Django built-in LoginView.

    Attributes:
        template_name (str): The name of the template to be used for rendering the login page.
        redirect_authenticated_user (bool): A flag indicating whether to redirect the user if already authenticated.

    Methods:
        post(request, *args, **kwargs): Handles the POST request for user authentication.
        get_success_url(): Returns the URL to redirect to after successful authentication.
    """

    template_name = "login.html"
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for user authentication.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.

        Raises:
            None

        Notes:
            - This method is responsible for authenticating the user based on the provided username and password.
            - If the user is authenticated and is a superuser, it logs in the user and redirects to the "customadmin:reported_posts_list" URL.
            - If the user is authenticated but not a superuser, it renders the login page again with the form data.
            - If the user is not authenticated, it renders the login page again with the form data.

        """
        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect("customadmin:reported_posts_list")
            else:
                return self.render_to_response(
                    self.get_context_data(form=self.get_form())
                )
        else:
            return self.render_to_response(self.get_context_data(form=self.get_form()))

    def get_success_url(self):
        """
        Returns the URL to redirect to after successful authentication.

        Parameters:
            None

        Returns:
            str: The URL to redirect to.

        Raises:
            None

        Notes:
            - This method is called after successful authentication.
            - It returns the URL to redirect to, which is "customadmin:reported_posts_list".
        """
        return reverse_lazy("customadmin:reported_posts_list")


class LogoutView(View):
    """
    A view class that handles user logout functionality.

    Methods:
        get(request): Handles the GET request for user logout.

    Attributes:
        None

    Notes:
        - This class extends the Django built-in View class.
        - The 'get' method logs out the user by calling the 'logout' function from Django's 'auth' module.
        - After logout, it redirects the user to the "customadmin:admin_login" URL.
    """

    def get(self, request):
        """
        Handles the GET request for user logout.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object.

        Raises:
            None

        Notes:
            - This method logs out the user by calling the 'logout' function from Django's 'auth' module.
            - After logout, it redirects the user to the "customadmin:admin_login" URL.
        """
        logout(request)
        return redirect("customadmin:admin_login")
