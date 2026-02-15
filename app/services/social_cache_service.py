from app import db
from app.models.social import CommunityPost, CommunityPostLike, CommunityComment
from app.utils.cache import LikeCache, CommentCache


def sync_likes_to_cache():
    """Sync all likes from DB to Redis for instant access"""
    try:
        # Get all likes grouped by post
        likes = db.session.query(
            CommunityPostLike.post_id, CommunityPostLike.user_id
        ).all()

        # Batch load into Redis
        for post_id, user_id in likes:
            LikeCache.like(user_id, post_id)

        print(f"Synced {len(likes)} likes to Redis cache")
    except Exception as e:
        print(f"Error syncing likes: {e}")


def sync_comment_counts_to_cache():
    """Sync comment counts from DB to Redis"""
    try:
        posts = CommunityPost.query.all()
        for post in posts:
            CommentCache.set_count(post.id, post.comments_count)

        print(f"Synced {len(posts)} post comment counts to Redis")
    except Exception as e:
        print(f"Error syncing comment counts: {e}")


def initialize_social_cache():
    """Initialize all social caching on startup"""
    print("Initializing social cache...")
    sync_likes_to_cache()
    sync_comment_counts_to_cache()
    print("Social cache initialized!")
