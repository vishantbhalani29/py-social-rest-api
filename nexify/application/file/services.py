import os

from django.db import transaction
from django.utils.crypto import get_random_string

from nexify.domain.file.models import File
from nexify.domain.file.services import FileServices
from nexify.domain.user.models import User
from nexify.infrastructure.storages.custom_storage import MediaStorage


class FileAppServices:
    """
    A class that provides services related to file operations.

    The FileAppServices class encapsulates the logic for uploading and creating or updating file objects. It utilizes the FileServices class for interacting with the File model and the MediaStorage class for storing files in S3.

    Attributes:
    - file_services (FileServices): An instance of the FileServices class for interacting with the File model.
    - media_storage (MediaStorage): An instance of the MediaStorage class for storing files in S3.

    Methods:
    - file_upload_s3: Uploads a file to S3 and returns the file URL.
    - create_or_update_file_from_file_obj: Creates or updates a file object based on a file object and user.

    """

    def __init__(self) -> None:
        self.file_services = FileServices()
        self.media_storage = MediaStorage()

    def file_upload_s3(self, file_obj, file_path_within_bucket: str):
        """
        Uploads a file to S3 and returns the file URL.

        Parameters:
        - file_obj: The file object to be uploaded.
        - file_path_within_bucket (str): The path of the file within the S3 bucket.

        Returns:
        - str: The URL of the uploaded file.

        """
        file_obj_copy = file_obj
        self.media_storage.save(file_path_within_bucket, file_obj_copy)
        file_url = self.media_storage.url(file_path_within_bucket)
        return file_url

    def create_or_update_file_from_file_obj(
        self, file_obj, user: User, file_instance: File = None
    ) -> File:
        """
        Creates or updates a file object based on a file object and user.

        Parameters:
        - file_obj: The file object to be uploaded.
        - user (User): The user who uploaded the file.
        - file_instance (File, optional): An existing file instance to be updated. Defaults to None.

        Returns:
        - File: The created or updated file object.

        Raises:
        - Exception: If an error occurs during the creation or update of the file object.

        """
        try:
            with transaction.atomic():
                file_path_within_bucket = os.path.join(
                    user.username, f"{get_random_string(15)}_{file_obj.name}"
                )
                file_url = self.file_upload_s3(
                    file_obj=file_obj, file_path_within_bucket=file_path_within_bucket
                )

                if file_instance:
                    file_instance.url = file_url
                    file_instance.save()
                    return file_instance

                file_factory = self.file_services.get_file_factory()
                file_obj = file_factory.build_entity_with_id(
                    uploader=user, url=file_url
                )
                file_obj.save()

                return file_obj
        except Exception as e:
            raise e
