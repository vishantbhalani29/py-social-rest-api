from typing import Type

from django.db.models.manager import BaseManager

from .models import File, FileFactory


class FileServices:
    """
    A class that provides services related to the File model.

    This FileServices class encapsulates the logic for interacting with the File model and provides methods for retrieving and manipulating File objects.

    Methods:
    - get_file_factory: Returns the FileFactory class, which can be used to create instances of the File model.
    - get_file_repo: Returns the BaseManager object for the File model, which can be used to query the database for File objects.
    - get_file_by_id: Retrieves a File object from the database based on its ID.

    """

    @staticmethod
    def get_file_factory() -> Type[FileFactory]:
        """
        Returns the FileFactory class, which can be used to create instances of the File model.

        Returns:
            Type[FileFactory]: The FileFactory class.

        """
        return FileFactory

    @staticmethod
    def get_file_repo() -> BaseManager[File]:
        """
        Returns the BaseManager object for the File model, which can be used to query the database for File objects.

        Returns:
            BaseManager[File]: The BaseManager object for the File model.

        """
        return File.objects

    def get_file_by_id(self, id: str) -> File:
        """
        Retrieves a File object from the database based on its ID.

        Parameters:
            id (str): The ID of the File object to retrieve.

        Returns:
            File: The File object with the specified ID.

        """
        return File.objects.get(id=id)
