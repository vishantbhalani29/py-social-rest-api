from dataclasses import dataclass

import sentry_sdk
from rest_framework import status


@dataclass(frozen=True)
class BaseException(Exception):
    item: str
    message: str
    status_code: int = status.HTTP_400_BAD_REQUEST

    def error_data(self) -> dict:
        error_data = {"item": self.item, "message": self.message}
        sentry_sdk.capture_exception(
            self, tags={"custom-exceptions": "custom-exceptions"}
        )

        return error_data

    def __str__(self):
        return "{}: {}".format(self.item, self.message)


# General exception classes with status codes


class Status400Exception(BaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_400_BAD_REQUEST)


class Status401Exception(BaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_401_UNAUTHORIZED)


class Status403Exception(BaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_403_FORBIDDEN)


class Status404Exception(BaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_404_NOT_FOUND)


class Status409Exception(BaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_409_CONFLICT)


class Status422Exception(BaseException):
    def __init__(self, item, message):
        super().__init__(
            item, message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class UserAlreadyExistsException(Status409Exception):
    pass


class PostNotFoundException(Status404Exception):
    pass


class UnauthorizedPostAccess(Status403Exception):
    pass


class PostCommentNotFoundException(Status404Exception):
    pass


class UnauthorizedPostCommentAccess(Status403Exception):
    pass


class UserNotFoundException(Status404Exception):
    pass


class UserFollowNotFoundException(Status404Exception):
    pass


class CannotFollowSelfException(Status400Exception):
    pass


class PostAlreadyReportedException(Status409Exception):
    pass


class InvalidPasswordException(Status400Exception):
    pass


class FileExtensionNotAllowedException(Status400Exception):
    pass
