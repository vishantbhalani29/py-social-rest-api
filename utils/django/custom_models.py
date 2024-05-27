from django.db import models


class ActivityTracking(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'modified_at' fields and an 'is_active' field
    to track the activity state of derived model instances.

    Attributes:
    - created_at (DateTimeField): The date and time when the record was created.
            Automatically set to the current date and time when the record is first created.
    - modified_at (DateTimeField): The date and time when the record was last modified.
            Automatically updated to the current date and time whenever the record is saved.
    - is_active (BooleanField): Flag to indicate whether the record is active or not.
            Defaults to True.

    Meta:
    - abstract (bool): Specifies that this model is an abstract base class and
            will not be used to create any database table.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
