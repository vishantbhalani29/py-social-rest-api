import inspect
from typing import Any, Dict, Union

import sentry_sdk
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    def __new__(
        cls,
        errors: Union[dict, Exception] = {},
        status_code: status = None,
        data: Dict[str, Any] = {},
        message: Union[str, Dict[str, str]] = "",
        for_error: bool = False,
        general_error: bool = False,
        is_partially_processed: bool = False,
    ) -> "APIResponse":
        cls.__init__(
            cls,
            message=message,
            errors=errors,
            status_code=status_code,
            data=data,
            for_error=for_error,
            general_error=general_error,
            is_partially_processed=is_partially_processed,
        )
        instance = super().__new__(cls)
        instance.message = message
        instance.errors = errors
        instance.status_code = status_code
        instance.data = data
        instance.for_error = for_error
        instance.is_partially_processed = is_partially_processed
        instance.caller_function = inspect.stack()[1].function
        if isinstance(errors, Exception):
            instance.errors = errors.args
            sentry_sdk.capture_exception(
                errors, tags={"catched-exceptions": "catched-exceptions"}
            )
        return instance.response_builder_callback()

    def __init__(
        self,
        message: Union[str, dict],
        errors={},
        status_code: status = None,
        data: Dict[str, Any] = {},
        for_error: bool = False,
        general_error: bool = False,
        is_partially_processed: bool = False,
    ) -> None:
        self.message = message
        self.errors = errors
        self.status_code = status_code
        self.data = data
        self.for_error = for_error
        self.caller_function = inspect.stack()[1].function
        self.general_error = general_error
        self.is_partially_processed = is_partially_processed

    def response_builder_callback(self):
        if self.for_error:
            return self.fail()
        else:
            return self.success()

    def struct_response(
        self,
        data: Dict[str, Any],
        success: bool,
        message: str,
        errors=None,
        is_partially_processed: bool = False,
    ) -> dict:
        response = dict(success=success, message=message, data=data)
        if errors:
            response["errors"] = errors
        if is_partially_processed:
            response["is_partially_processed"] = is_partially_processed
        return response

    def success_message(self):
        return f'{self.caller_function.replace("_", "-").title()} Successful.'

    def success(self) -> Response:
        """This method will create custom response for success event with response status 200."""
        success_message = self.message if self.message else self.success_message()
        is_partially_processed = True if self.is_partially_processed else False
        response_data = self.struct_response(
            data=self.data,
            success=True,
            message=success_message,
            is_partially_processed=is_partially_processed,
        )
        success_status = self.status_code if self.status_code else status.HTTP_200_OK
        return Response(response_data, status=success_status)

    def fail(self) -> Response:
        """This method will create custom response for failure event with custom response status."""
        error_message = (
            self.message[next(iter(self.message))][0]
            if isinstance(self.message, dict)
            else self.message
        )
        if self.general_error:
            error_message = settings.GENERAL_ERROR_MESSAGE
        response_data = self.struct_response(
            data={}, success=False, message=error_message, errors=self.errors
        )
        return Response(response_data, status=self.status_code)
