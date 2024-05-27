from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    A class that represents a storage backend for media files using S3Boto3Storage.

    This class inherits from the S3Boto3Storage class provided by the 'storages' package.
    It is specifically designed to be used as the storage backend for media files in Django projects.

    Attributes:
        bucket_name (str): The name of the S3 bucket where the media files will be stored.
        location (str): The location within the bucket where the media files will be stored.
        file_overwrite (bool): A flag indicating whether existing files should be overwritten when uploading.

    Note:
        This class assumes that the 'settings' module from Django is properly configured,
        and that the 'MINIO_STORAGE_MEDIA_BUCKET_NAME' setting is defined with the desired bucket name.

    Example usage:
        storage = MediaStorage()
        storage.save('my_image.jpg', file_object)

        This will save the 'file_object' as 'my_image.jpg' in the configured S3 bucket.

    """

    bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
    location = "media"
    file_overwrite = True
