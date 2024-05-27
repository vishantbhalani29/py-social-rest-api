from django.conf import settings
from django.db import transaction
from django.utils.timezone import localtime

from nexify.domain.post.models import Post
from nexify.domain.post.services import PostServices
from nexify.infrastructure.emailer.services import MailerServices
from utils.django.exceptions import PostNotFoundException


class DeleteReportedPostServices:
    """
    A class that provides services for deleting reported posts.

    This class contains methods for sending a post deletion email to the user who created the post and deleting the reported post.

    Methods:
    - send_post_deletion_mail(post_obj: Post) -> None:
        Sends a post deletion email to the user who created the post.

    - delete_reported_post(post_id: str) -> None:
        Deletes the reported post with the specified ID.

    Raises:
    - Exception: If an error occurs while sending the email or deleting the post.
    - PostNotFoundException: If the post with the specified ID is not found.

    """

    def send_post_deletion_mail(self, post_obj: Post) -> None:
        """
        Sends a post deletion email to the user who created the post.

        Parameters:
        - post_obj (Post): The Post object representing the post to be deleted.

        Returns:
        None

        Raises:
        Exception: If an error occurs while sending the email.

        """
        try:
            template_data = dict(
                subject=settings.POST_DELETE_SUBJECT,
                user_name=post_obj.user.username,
                post_description=post_obj.description,
                deletion_date=localtime().strftime("%B %d, %Y"),
            )
            MailerServices().send_mail(
                email=post_obj.user.email,
                subject=template_data.get("subject"),
                template_data=template_data,
                template_id=settings.POST_DELETE_EMAIL_TEMPLATE,
            )
        except Exception as e:
            raise e

    def delete_reported_post(self, post_id: str) -> None:
        """
        Deletes the reported post with the specified ID.

        Parameters:
        - post_id (str): The ID of the reported post to be deleted.

        Returns:
        None

        Raises:
        - Exception: If an error occurs while deleting the post.
        - PostNotFoundException: If the post with the specified ID is not found.

        """
        with transaction.atomic():
            post_obj = (
                PostServices()
                .get_post_repo()
                .filter(id=post_id, is_active=True)
                .first()
            )
            if post_obj:
                post_obj.delete()
                self.send_post_deletion_mail(post_obj=post_obj)
            else:
                raise PostNotFoundException(
                    item="post-not-found-exception", message="Post not found."
                )
