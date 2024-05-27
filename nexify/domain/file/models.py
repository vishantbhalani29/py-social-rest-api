import uuid
from dataclasses import dataclass
from typing import Any, Dict

from django.db import models

from nexify.domain.user.models import User
from utils.django import custom_models


@dataclass(frozen=True)
class FileID:
    """
    A class representing the ID of a File.

    Attributes:
        value (uuid.UUID): The unique identifier value of the File ID.

    """

    value: uuid.UUID


# ----------------------------------------------------------------------
# File Model
# ----------------------------------------------------------------------


class File(custom_models.ActivityTracking):
    """
    A custom File model that extends the ActivityTracking class and includes additional fields.

    This File class represents a file uploaded by a user. It contains fields for the file's ID, uploader, URL, and metadata.

    Attributes:
    - id (UUIDField): The unique identifier for the file, automatically generated using UUID4.
    - uploader (ForeignKey): The user who uploaded the file, referenced from the User model.
    - url (TextField): The URL of the file.
    - meta_data (JSONField): Additional metadata associated with the file, stored as JSON.

    Meta:
    - verbose_name (str): The human-readable name of the model, set to "File".
    - verbose_name_plural (str): The plural form of the verbose_name, set to "Files".
    - db_table (str): The name of the database table for this model, set to "file".
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField(verbose_name="file_url")
    meta_data = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
        db_table = "file"


class FileFactory:
    """
    A factory class for creating instances of the File model.

    This FileFactory class provides static methods for building File entities with different parameters. It is used to encapsulate the creation logic and provide a convenient interface for creating File objects.

    Methods:
    - build_entity: Creates a File entity with the given parameters.
    - build_entity_with_id: Creates a File entity with a generated FileID and the given parameters.

    """

    @staticmethod
    def build_entity(
        id: FileID,
        uploader: User,
        url: str,
        meta_data: Dict[str, Any] = {},
    ) -> File:
        return File(
            id=id.value,
            uploader=uploader,
            url=url,
            meta_data=meta_data,
        )

    @classmethod
    def build_entity_with_id(
        cls,
        uploader: User,
        url: str,
        meta_data: Dict[str, Any] = {},
    ) -> File:
        entity_id = FileID(uuid.uuid4())
        return cls.build_entity(
            id=entity_id,
            uploader=uploader,
            url=url,
            meta_data=meta_data,
        )
