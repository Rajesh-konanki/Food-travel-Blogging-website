from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from forms import PostForm
from models import Category, Comment, Post
from utils import parse_tags, save_image, unique_slug

dashboard_bp = Blueprint("dashboard", __name__)


def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return wrapper


def populate_category_choices(form):
    categories = Category.query.order_by(Category.name.asc()).all()
    if not categories:
        default_category = Category(name="General", slug="general", description="General posts")
        db.session.add(default_category)
        db.session.commit()
        categories = [default_category]
    form.category.choices = [(cat.id, cat.name) for cat in categories]


@dashboard_bp.route("/dashboard")
@admin_required
def dashboard_home():
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status="published").count()
    draft_posts = Post.query.filter_by(status="draft").count()
    total_comments = Comment.query.count()
    pending_comments = Comment.query.filter_by(approved=False).count()
    total_views = db.session.query(db.func.coalesce(db.func.sum(Post.views), 0)).scalar() or 0
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    return render_template(
        "dashboard.html",
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=draft_posts,
        total_comments=total_comments,
        pending_comments=pending_comments,
        total_views=total_views,
        recent_posts=recent_posts,
    )


@dashboard_bp.route("/dashboard/posts")
@admin_required
def posts_list():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("create_post.html", form=None, posts=posts, mode="list")


@dashboard_bp.route("/dashboard/posts/create", methods=["GET", "POST"])
@admin_required
def create_post():
    form = PostForm()
    populate_category_choices(form)
    if form.validate_on_submit():
        filename = save_image(form.cover_image.data, current_app.config["UPLOAD_FOLDER"])
        post = Post(
            title=form.title.data.strip(),
            slug=unique_slug(Post, form.title.data),
            content=form.content.data.strip(),
            status=form.status.data,
            category_id=form.category.data,
            author_id=current_user.id,
            cover_image=filename,
        )
        post.tags = parse_tags(form.tags.data)
        post.refresh_excerpt()
        db.session.add(post)
        db.session.commit()
        flash("Post created successfully.", "success")
        return redirect(url_for("dashboard.dashboard_home"))
    return render_template("create_post.html", form=form, mode="create")


@dashboard_bp.route("/dashboard/posts/<int:post_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    populate_category_choices(form)
    if request.method == "GET":
        form.tags.data = ", ".join(tag.name for tag in post.tags)
    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.slug = unique_slug(Post, form.title.data, current_id=post.id)
        post.content = form.content.data.strip()
        post.status = form.status.data
        post.category_id = form.category.data
        new_image = save_image(form.cover_image.data, current_app.config["UPLOAD_FOLDER"])
        if new_image:
            post.cover_image = new_image
        post.tags = parse_tags(form.tags.data)
        post.refresh_excerpt()
        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("dashboard.dashboard_home"))
    return render_template("edit_post.html", form=form, post=post)


@dashboard_bp.route("/dashboard/posts/<int:post_id>/delete", methods=["POST"])
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("dashboard.dashboard_home"))


@dashboard_bp.route("/dashboard/comments")
@admin_required
def pending_comments():
    comments = Comment.query.filter_by(approved=False).order_by(Comment.created_at.desc()).all()
    return render_template("dashboard.html", comments=comments, comments_mode=True)


@dashboard_bp.route("/dashboard/comments/<int:comment_id>/approve", methods=["POST"])
@admin_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.approved = True
    db.session.commit()
    flash("Comment approved.", "success")
    return redirect(url_for("dashboard.pending_comments"))


@dashboard_bp.route("/dashboard/comments/<int:comment_id>/delete", methods=["POST"])
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", "info")
    return redirect(url_for("dashboard.pending_comments"))
