from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    """
    UserPagination class is a custom pagination class that extends the PageNumberPagination class from the rest_framework.pagination module.

    Attributes:
        - page_size (int): The number of items to be displayed per page. Default value is 5.
        - page_size_query_param (str): The query parameter name for specifying the page size. Default value is "page_size".
        - max_page_size (int): The maximum allowed page size. Default value is 100.

    This class provides pagination functionality for the User model in the API.

    Example usage:
        pagination_class = UserPagination

    By using this class as the pagination_class in a view or viewset, the API response will be paginated according to the specified page size and query parameters.

    Note: This class inherits all the methods and attributes from the PageNumberPagination class.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100
