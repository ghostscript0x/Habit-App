from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.models.social import CommunityPost, CommunityPostLike, CommunityComment, UserReport
from datetime import datetime, timezone
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

community_bp = Blueprint('community', __name__, url_prefix='/community')


class PostForm(FlaskForm):
    content = TextAreaField('Share something motivational...', validators=[DataRequired()])
    is_anonymous = SelectField('Post As', choices=[('false', 'With Username'), ('true', 'Anonymous')], default='false')
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Add Comment')


class ReportForm(FlaskForm):
    reason = SelectField('Reason', choices=[
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit Report')


@community_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    posts = CommunityPost.query.filter_by(is_approved=True)\
        .order_by(CommunityPost.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('community/index.html', posts=posts)


@community_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    
    if form.validate_on_submit():
        post = CommunityPost()
        post.user_id = current_user.id
        post.content = form.content.data
        post.is_anonymous = form.is_anonymous.data == 'true'
        
        if current_user.is_admin:
            post.is_approved = True
        else:
            post.is_approved = True
        
        db.session.add(post)
        
        current_user.points += 5
        db.session.commit()
        
        flash('Post shared! +5 points', 'success')
        return redirect(url_for('community.index'))
    
    return render_template('community/create.html', form=form)


@community_bp.route('/post/<post_id>/like', methods=['POST'])
@login_required
def like(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    
    existing_like = CommunityPostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
    else:
        like = CommunityPostLike()
        like.post_id = post_id
        like.user_id = current_user.id
        db.session.add(like)
        post.likes_count += 1
    
    db.session.commit()
    return jsonify({'likes': post.likes_count})


@community_bp.route('/post/<post_id>/comment', methods=['GET', 'POST'])
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
        current_user.points += 2
        db.session.commit()
        
        flash('Comment added! +2 points', 'success')
        return redirect(url_for('community.post', post_id=post_id))
    
    comments = CommunityComment.query.filter_by(post_id=post_id)\
        .order_by(CommunityComment.created_at.asc()).all()
    
    return render_template('community/post.html', post=post, form=form, comments=comments)


@community_bp.route('/post/<post_id>')
@login_required
def post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    comments = CommunityComment.query.filter_by(post_id=post_id)\
        .order_by(CommunityComment.created_at.asc()).all()
    return render_template('community/post.html', post=post, comments=comments, form=CommentForm())


@community_bp.route('/post/<post_id>/report', methods=['GET', 'POST'])
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
        
        flash('Report submitted. Thank you!', 'success')
        return redirect(url_for('community.index'))
    
    return render_template('community/report.html', form=form, post=post)


@community_bp.route('/achievements')
@login_required
def achievements():
    from app.models import UserAchievement, Achievement
    user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    all_achievements = Achievement.query.all()
    
    user_achievement_ids = [ua.achievement_id for ua in user_achievements]
    
    return render_template('community/achievements.html',
                          user_achievements=user_achievements,
                          all_achievements=all_achievements,
                          user_achievement_ids=user_achievement_ids)


@community_bp.route('/achievements/<achievement_id>/share')
@login_required
def share_achievement(achievement_id):
    from app.models import UserAchievement
    ua = UserAchievement.query.filter_by(user_id=current_user.id, achievement_id=achievement_id).first()
    
    if not ua:
        flash('Achievement not found.', 'danger')
        return redirect(url_for('community.achievements'))
    
    achievement = ua.achievement
    
    post = CommunityPost()
    post.user_id = current_user.id
    post.content = f"I just earned the '{achievement.name}' achievement! {achievement.description}"
    post.is_anonymous = False
    post.is_approved = True
    db.session.add(post)
    db.session.commit()
    
    flash('Achievement shared to community!', 'success')
    return redirect(url_for('community.index'))
