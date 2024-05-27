from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import ListView, View

from custom_admin.services.helper_services import DeleteReportedPostServices
from nexify.domain.post.services import PostServices


class ReportedPostsList(LoginRequiredMixin, ListView):
    """
    A class representing a view for displaying a list of reported posts.

    This class inherits from the LoginRequiredMixin and ListView classes provided by Django. It is used to render a template named 'dashboard.html' and display a list of reported posts.

    Attributes:
    - template_name (str): The name of the template to be rendered.
    - context_object_name (str): The name of the context variable containing the reported posts.
    - login_url (str): The URL to redirect to if the user is not logged in.

    Methods:
    - get_queryset() -> QuerySet:
        Returns the queryset of reported posts to be displayed.

    """

    template_name = "dashboard.html"
    context_object_name = "reported_posts"
    login_url = "customadmin:admin_login"

    def get_queryset(self):
        """
        Returns the queryset of reported posts to be displayed.

        Returns:
            QuerySet: The queryset of reported posts to be displayed.
        """
        return (
            PostServices()
            .get_post_repo()
            .filter(is_active=True, is_reported=True, report_count__gt=0)
            .order_by("-report_count")
        )


class DeleteReportedPostView(View):
    """
    A view class for deleting reported posts.

    This class handles the deletion of reported posts by utilizing the DeleteReportedPostServices class. It provides a delete method that is called when a DELETE request is made to the corresponding URL.

    Attributes:
    - delete_reported_post_services (DeleteReportedPostServices): An instance of the DeleteReportedPostServices class for performing the deletion of reported posts.

    Methods:
    - delete(request, post_id): Handles the DELETE request for deleting a reported post. It calls the delete_reported_post method of the delete_reported_post_services instance to perform the deletion. If successful, it returns a JSON response with a success message. If an error occurs, it returns a JSON response with an error message and a status code of 400.

    """

    def delete(self, request, post_id):
        """
        Handles the DELETE request for deleting a reported post.

        Parameters:
        - request (HttpRequest): The HTTP request object.
        - post_id (str): The ID of the reported post to be deleted.

        Returns:
        - JsonResponse: A JSON response with a success message if the post is deleted successfully. If an error occurs, it returns a JSON response with an error message and a status code of 400.

        Raises:
        - Exception: If an error occurs while deleting the post.

        """
        try:
            delete_reported_post_services = DeleteReportedPostServices()
            delete_reported_post_services.delete_reported_post(post_id=post_id)
            messages.success(self.request, "Post has been deleted successfully.")
            return JsonResponse({"message": "Post deleted successfully."})
        except Exception as e:
            messages.error(
                self.request, "Something went wrong, Please try again letter!"
            )
            return JsonResponse({"error": "Failed to delete post."}, status=400)
