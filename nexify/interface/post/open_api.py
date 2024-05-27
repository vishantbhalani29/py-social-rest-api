from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema

from .serializers import (
    PostCommentCreateSerializer,
    PostCommentSerializer,
    PostCreateSerializer,
    PostSerializer,
    ReportedPostSerializer,
)

post_tags = ["Post-Module"]

post_id = OpenApiParameter(
    name="post_id",
    type=str,
    location=OpenApiParameter.QUERY,
    description="A post ID string is required to identify the Post.",
)

search_filter_param = OpenApiParameter(
    name="search",
    type=str,
    location=OpenApiParameter.QUERY,
    description="Post searching",
)

sorting_param = OpenApiParameter(
    name="sort_by",
    type=str,
    location=OpenApiParameter.QUERY,
    description="Post sorting",
    examples=[
        OpenApiExample("likes_count", value="likes_count"),
        OpenApiExample("-likes_count", value="-likes_count"),
        OpenApiExample("comments_count", value="comments_count"),
        OpenApiExample("-comments_count", value="-comments_count"),
    ],
)

post_list_extension = extend_schema(
    tags=post_tags,
    parameters=[search_filter_param, sorting_param],
    responses={200: PostSerializer},
)

post_create_extension = extend_schema(
    tags=post_tags,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "file": {"type": "string", "format": "binary"},
            },
            "required": ["description"],
        }
    },
    responses={200: PostSerializer},
)

post_retrieve_extension = extend_schema(
    tags=post_tags,
    responses={200: PostSerializer},
)

post_update_extension = extend_schema(
    tags=post_tags,
    responses={200: PostSerializer},
)

post_delete_extension = extend_schema(
    tags=post_tags,
    responses={200: {}},
)

post_comment_create_extension = extend_schema(
    tags=post_tags,
    parameters=[post_id],
    request=PostCommentCreateSerializer,
    responses={200: PostCommentSerializer},
)

post_comment_list_extension = extend_schema(
    tags=post_tags,
    responses={200: PostCommentSerializer},
)

post_comment_delete_extension = extend_schema(
    tags=post_tags,
    responses={200: {}},
)

post_like_unlike_extension = extend_schema(
    tags=post_tags,
    responses={200: PostSerializer},
)

post_report_extension = extend_schema(
    tags=post_tags,
    responses={200: ReportedPostSerializer},
)

list_recommend_posts_extension = extend_schema(
    tags=post_tags,
    responses={200: PostSerializer},
)
