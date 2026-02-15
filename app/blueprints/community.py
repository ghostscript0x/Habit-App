from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.models.social import (
    CommunityPost,
    CommunityPostLike,
    CommunityComment,
    UserReport,
)
from datetime import datetime, timezone
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.utils.cache import cache_get, cache_set, delete_cache, LikeCache, CommentCache

community_bp = Blueprint("community", __name__, url_prefix="/community")


class PostForm(FlaskForm):
    content = TextAreaField(
        "Share something motivational...", validators=[DataRequired()]
    )
    is_anonymous = SelectField(
        "Post As",
        choices=[("false", "With Username"), ("true", "Anonymous")],
        default="false",
    )
    submit = SubmitField("Post")


class CommentForm(FlaskForm):
    content = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Add Comment")


class ReportForm(FlaskForm):
    reason = SelectField(
        "Reason",
        choices=[
            ("spam", "Spam"),
            ("harassment", "Harassment"),
            ("inappropriate", "Inappropriate Content"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit Report")


@community_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 20
    cache_key = f"community:posts:page:{page}"

    posts = cache_get(cache_key)
    if posts is None:
        posts = (
            CommunityPost.query.filter_by(is_approved=True)
            .order_by(CommunityPost.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        cache_set(cache_key, posts, timeout=60)

    # Build set of liked post IDs for fast lookup
    liked_post_ids = set()

    # Preload like counts and statuses from Redis for speed
    for post in posts.items:
        # Get cached like count
        cached_count = LikeCache.get_count(post.id)
        if cached_count:
            post.likes_count = cached_count
        else:
            # Initialize cache with DB count
            LikeCache.set_count(post.id, post.likes_count)

        # Get cached comment count
        cached_comments = CommentCache.get_count(post.id)
        if cached_comments:
            post.comments_count = cached_comments
        else:
            CommentCache.set_count(post.id, post.comments_count)

        # Check if user liked this post (from Redis)
        if LikeCache.is_liked(current_user.id, post.id):
            liked_post_ids.add(post.id)

    return render_template(
        "community/index.html", posts=posts, liked_post_ids=liked_post_ids
    )


@community_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()

    if form.validate_on_submit():
        post = CommunityPost()
        post.user_id = current_user.id
        post.content = form.content.data
        post.is_anonymous = form.is_anonymous.data == "true"

        if current_user.is_admin:
            post.is_approved = True
        else:
            post.is_approved = True

        db.session.add(post)

        current_user.points = (current_user.points or 0) + 5
        db.session.commit()

        delete_cache("community:posts:*")

        flash("Post shared! +5 points", "success")
        return redirect(url_for("community.index"))

    return render_template("community/create.html", form=form)


@community_bp.route("/post/<post_id>/like", methods=["POST"])
@login_required
def like(post_id):
    # Check cache first (super fast O(1))
    is_liked = LikeCache.is_liked(current_user.id, post_id)

    # Get post for DB update (background)
    post = CommunityPost.query.get_or_404(post_id)

    if is_liked:
        # Unlike - remove from both cache and DB
        LikeCache.unlike(current_user.id, post_id)
        existing_like = CommunityPostLike.query.filter_by(
            post_id=post_id, user_id=current_user.id
        ).first()
        if existing_like:
            db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        new_count = post.likes_count
    else:
        # Like - add to both cache and DB
        LikeCache.like(current_user.id, post_id)
        like = CommunityPostLike()
        like.post_id = post_id
        like.user_id = current_user.id
        db.session.add(like)
        post.likes_count += 1
        new_count = post.likes_count

    db.session.commit()

    # Return cached count for instant response
    cached_count = LikeCache.get_count(post_id)
    return jsonify({"likes": cached_count if cached_count > 0 else new_count})


@community_bp.route("/post/<post_id>/comment", methods=["GET", "POST"])
@login_required
def comment(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = CommunityComment()
        comment.post_id = post_id
        comment.user_id = current_user.id
        comment.content = form.content.data
        db.session.add(comment)

        post.comments_count += 1
        current_user.points = (current_user.points or 0) + 2

        # Update cache instantly
        CommentCache.increment(post_id)

        db.session.commit()

        flash("Comment added! +2 points", "success")
        return redirect(url_for("community.post", post_id=post_id))

    comments = (
        CommunityComment.query.filter_by(post_id=post_id)
        .order_by(CommunityComment.created_at.asc())
        .all()
    )

    return render_template(
        "community/post.html", post=post, form=form, comments=comments
    )


@community_bp.route("/post/<post_id>")
@login_required
def post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    comments = (
        CommunityComment.query.filter_by(post_id=post_id)
        .order_by(CommunityComment.created_at.asc())
        .all()
    )

    # Use Redis for instant like check
    is_liked = LikeCache.is_liked(current_user.id, post_id)

    # Get cached counts
    cached_likes = LikeCache.get_count(post_id)
    if cached_likes:
        post.likes_count = cached_likes

    cached_comments = CommentCache.get_count(post_id)
    if cached_comments:
        post.comments_count = cached_comments

    return render_template(
        "community/post.html",
        post=post,
        comments=comments,
        form=CommentForm(),
        is_liked=is_liked,
    )


@community_bp.route("/post/<post_id>/report", methods=["GET", "POST"])
@login_required
def report(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    form = ReportForm()

    if form.validate_on_submit():
        report = UserReport()
        report.reporter_id = current_user.id
        report.reported_user_id = post.user_id
        report.reason = form.reason.data
        report.description = form.description.data
        db.session.add(report)
        db.session.commit()

        flash("Report submitted. Thank you!", "success")
        return redirect(url_for("community.index"))

    return render_template("community/report.html", form=form, post=post)


@community_bp.route("/achievements")
@login_required
def achievements():
    from app.models import UserAchievement, Achievement

    user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    all_achievements = Achievement.query.all()

    user_achievement_ids = [ua.achievement_id for ua in user_achievements]

    return render_template(
        "community/achievements.html",
        user_achievements=user_achievements,
        all_achievements=all_achievements,
        user_achievement_ids=user_achievement_ids,
    )


@community_bp.route("/achievements/<achievement_id>/share")
@login_required
def share_achievement(achievement_id):
    from app.models import UserAchievement

    ua = UserAchievement.query.filter_by(
        user_id=current_user.id, achievement_id=achievement_id
    ).first()

    if not ua:
        flash("Achievement not found.", "danger")
        return redirect(url_for("community.achievements"))

    achievement = ua.achievement

    post = CommunityPost()
    post.user_id = current_user.id
    post.content = (
        f"I just earned the '{achievement.name}' achievement! {achievement.description}"
    )
    post.is_anonymous = False
    post.is_approved = True
    db.session.add(post)
    db.session.commit()

    flash("Achievement shared to community!", "success")
    return redirect(url_for("community.index"))
