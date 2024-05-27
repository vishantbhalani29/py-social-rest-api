from django.urls import path

from custom_admin.views.dashboard_view import DeleteReportedPostView, ReportedPostsList

urlpatterns = [
    path("dashboard/", ReportedPostsList.as_view(), name="reported_posts_list"),
    path(
        "delete-reported-post/<post_id>",
        DeleteReportedPostView.as_view(),
        name="delete_reported_post",
    ),
]
