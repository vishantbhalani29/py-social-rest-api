import django_filters
from django.db.models import Q

from nexify.domain.post.models import Post


class PostFilters(django_filters.FilterSet):
    """
    A class representing filters for the Post model.

    This class extends the django_filters.FilterSet class to provide filtering capabilities for the Post model.

    Attributes:
    - model (Model): The model class to which the filterset is applied, set to Post.
    - fields (list): The list of fields on which the filters are applied, set to ["user", "description"].

    Filter Fields:
    - search (CharFilter): A filter for searching posts based on the description or user's first or last name.
    - sort_by (CharFilter): A filter for sorting posts based on a specified field.

    Methods:
    - search_filter(queryset, name, value): A method to filter the queryset based on the search filter.
    - sort_by_filter(queryset, name, value): A method to sort the queryset based on the sort_by filter.
    """

    class Meta:
        model = Post
        fields = ["user", "description"]

    search = django_filters.CharFilter(method="search_filter", label="search")

    sort_by = django_filters.CharFilter(method="sort_by_filter", label="sort_by")

    def search_filter(self, queryset, name, value):
        """
        Filter the queryset based on the search filter.

        This method takes in a queryset, name, and value as parameters. It filters the queryset based on the search filter, which searches for posts based on the description or user's first or last name. The search is case-insensitive.

        Parameters:
        - queryset (QuerySet): The queryset to be filtered.
        - name (str): The name of the filter.
        - value (str): The value to be searched.

        Returns:
        - QuerySet: The filtered queryset.

        Example:
        search_filter(queryset, name, value)
        """
        return queryset.filter(
            Q(description__icontains=value)
            | Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
        ).distinct()

    def sort_by_filter(self, queryset, name, value):
        """
        Sort the queryset based on the sort_by filter.

        This method takes in a queryset, name, and value as parameters. It sorts the queryset based on the sort_by filter, which specifies the field to sort the posts by.

        Parameters:
        - queryset (QuerySet): The queryset to be sorted.
        - name (str): The name of the filter.
        - value (str): The field to sort the posts by.

        Returns:
        - QuerySet: The sorted queryset.

        Example:
        sort_by_filter(queryset, name, value)
        """
        return queryset.order_by(value)
