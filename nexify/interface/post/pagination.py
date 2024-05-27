from rest_framework.pagination import PageNumberPagination


class PostPagination(PageNumberPagination):
    """
    A custom pagination class for paginating posts.

    This class extends the 'PageNumberPagination' class from the 'rest_framework.pagination' module.

    Attributes:
        page_size (int): The number of posts to be displayed per page. Default is 5.
        page_size_query_param (str): The query parameter name for specifying the page size. Default is "page_size".
        max_page_size (int): The maximum number of posts that can be displayed per page. Default is 100.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100
