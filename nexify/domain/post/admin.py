from django.contrib import admin

from .models import Post, PostComment, PostLike, ReportedPost

admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(PostLike)
admin.site.register(ReportedPost)
