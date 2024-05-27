import random
from collections import defaultdict

from django.conf import settings
from django.db import transaction

from nexify.application.post.services import (
    PostAppServices,
    PostLikeAppServices,
    PostRecommendationAppServices,
)
from nexify.application.user.services import UserAppServices
from nexify.celery import app


@app.task
def create_post_recommendations():
    """
    Task: Generate post recommendations for users based on their liked posts.

    This function fetches a list of non-staff and non-superuser users, retrieves the liked posts for each user,
    and generates post recommendations for each user by excluding the posts they have already liked.
    The recommendations are limited to a specified number of posts defined in the settings.
    It then updates or creates recommendations for each user based on the generated recommendations.

    Returns:
        None

    Raises:
        Any exception that occurs during the process will be caught and printed with an error message.
    """
    post_app_services = PostAppServices()
    post_like_app_services = PostLikeAppServices()
    post_recommendation_app_services = PostRecommendationAppServices()
    user_app_services = UserAppServices()

    try:
        with transaction.atomic():
            users = user_app_services.list_users().exclude(
                is_staff=True, is_superuser=True
            )
            user_ids = [user.id for user in users]

            # Fetch all liked posts for the users in a single query
            liked_posts = (
                post_like_app_services.list_post_likes()
                .filter(user_id__in=user_ids)
                .values("user_id", "post_id")
            )

            # Create a dictionary to map users to their liked post IDs
            user_liked_posts = defaultdict(set)
            for liked_post in liked_posts:
                user_liked_posts[liked_post["user_id"]].add(liked_post["post_id"])

            # Fetch all posts in one go
            all_posts = list(post_app_services.list_posts())

            # Dictionary to store user recommendations
            user_recommendations = {}

            for user in users:
                # Shuffle posts for unique recommendations
                random.shuffle(all_posts)
                liked_posts_ids = user_liked_posts[user.id]
                recommend_posts = [
                    post for post in all_posts if post.id not in liked_posts_ids
                ][: settings.RECOMMEND_POST_SIZE]
                user_recommendations[user] = recommend_posts

            # Fetch existing recommendations in bulk
            existing_recommendations = post_recommendation_app_services.post_recommendation_services.get_post_recommendation_repo().filter(
                user_id__in=user_ids
            )

            existing_recommendations_dict = {
                rec.user_id: rec for rec in existing_recommendations
            }

            # Update or create recommendations
            for user in users:
                if user.id in existing_recommendations_dict:
                    user_recommendation = existing_recommendations_dict[user.id]
                    user_recommendation.recommend_posts.clear()
                    user_recommendation.recommend_posts.add(*user_recommendations[user])
                else:
                    user_recommendation = post_recommendation_app_services.post_recommendation_services.get_post_recommendation_repo().create(
                        user=user
                    )
                    user_recommendation.recommend_posts.add(*user_recommendations[user])

    except Exception as e:
        print(str(e), "Error while creating post recommendations.")
