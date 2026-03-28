from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from extensions import db
from forms import CommentForm
from models import Category, Comment, Post, Tag

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.options(joinedload(Post.author), joinedload(Post.category))
        .filter_by(status="published")
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    )
    featured_post = posts.items[0] if posts.items else None
    return render_template("index.html", posts=posts, featured_post=featured_post, term=None)


@main_bp.route("/post/<slug>")
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, status="published").first_or_404()
    post.views += 1
    db.session.commit()
    related_posts = (
        Post.query.filter(
            Post.category_id == post.category_id,
            Post.id != post.id,
            Post.status == "published",
        )
        .order_by(Post.created_at.desc())
        .limit(3)
        .all()
    )
    comments = (
        Comment.query.filter_by(post_id=post.id, approved=True)
        .order_by(Comment.created_at.desc())
        .all()
    )
    form = CommentForm()
    return render_template(
        "post_detail.html",
        post=post,
        related_posts=related_posts,
        comments=comments,
        form=form,
    )


@main_bp.route("/category/<slug>")
def by_category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.filter_by(category_id=category.id, status="published")
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    )
    return render_template("index.html", posts=posts, featured_post=None, term=None, category=category)


@main_bp.route("/tag/<slug>")
def by_tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.join(Post.tags)
        .filter(Tag.id == tag.id, Post.status == "published")
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    )
    return render_template("index.html", posts=posts, featured_post=None, term=None, tag=tag)


@main_bp.route("/search")
def search():
    term = request.args.get("q", "", type=str).strip()
    page = request.args.get("page", 1, type=int)
    query = Post.query.filter_by(status="published")
    if term:
        like = f"%{term}%"
        query = query.filter(or_(Post.title.ilike(like), Post.content.ilike(like)))
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    return render_template("index.html", posts=posts, featured_post=None, term=term)


@main_bp.route("/post/<slug>/comment", methods=["POST"])
def submit_comment(slug):
    post = Post.query.filter_by(slug=slug, status="published").first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            author_name=form.author_name.data,
            author_email=form.author_email.data,
            post_id=post.id,
            approved=False,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Comment submitted and pending approval.", "info")
    else:
        flash("Please submit a valid comment.", "danger")
    return redirect(url_for("main.post_detail", slug=slug))
