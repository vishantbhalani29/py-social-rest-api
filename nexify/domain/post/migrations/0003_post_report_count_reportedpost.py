# Generated by Django 4.2.11 on 2024-05-01 06:31

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("post", "0002_postlike_postcomment"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="report_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ReportedPost",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="post.post"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "ReportedPost",
                "verbose_name_plural": "ReportedPosts",
                "db_table": "reported_post",
            },
        ),
    ]
