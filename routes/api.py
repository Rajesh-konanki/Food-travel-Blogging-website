from functools import wraps

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from extensions import db
from models import Category, Comment, Post, Tag
from utils import parse_tags, post_to_dict, unique_slug

api_bp = Blueprint("api", __name__)


def admin_only(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            return jsonify({"error": "admin required"}), 403
        return func(*args, **kwargs)

    return wrapper


@api_bp.get("/posts")
def api_posts():
    page = request.args.get("page", 1, type=int)
    category_slug = request.args.get("category")
    tag_slug = request.args.get("tag")
    term = request.args.get("q", "")

    query = Post.query.filter_by(status="published")
    if category_slug:
        query = query.join(Post.category).filter(Category.slug == category_slug)
    if tag_slug:
        query = query.join(Post.tags).filter(Tag.slug == tag_slug)
    if term:
        like = f"%{term}%"
        query = query.filter(or_(Post.title.ilike(like), Post.content.ilike(like)))

    paginated = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6, error_out=False)
    return jsonify(
        {
            "items": [post_to_dict(post) for post in paginated.items],
            "page": paginated.page,
            "pages": paginated.pages,
            "total": paginated.total,
        }
    )


@api_bp.get("/posts/<int:post_id>")
def api_post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if post.status != "published":
        return jsonify({"error": "post not published"}), 404
    return jsonify(post_to_dict(post))


@api_bp.post("/posts")
@login_required
def api_create_post():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400
    post = Post(
        title=title,
        slug=unique_slug(Post, title),
        content=content,
        status=data.get("status", "draft"),
        author_id=current_user.id,
        category_id=data.get("category_id"),
    )
    post.tags = parse_tags(data.get("tags", ""))
    post.refresh_excerpt()
    db.session.add(post)
    db.session.commit()
    return jsonify(post_to_dict(post)), 201


@api_bp.put("/posts/<int:post_id>")
@login_required
def api_update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.role != "admin" and post.author_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(silent=True) or {}
    if "title" in data:
        post.title = data["title"].strip()
        post.slug = unique_slug(Post, post.title, current_id=post.id)
    if "content" in data:
        post.content = data["content"].strip()
    if "status" in data:
        post.status = data["status"]
    if "category_id" in data:
        post.category_id = data["category_id"]
    if "tags" in data:
        post.tags = parse_tags(data.get("tags", ""))
    post.refresh_excerpt()
    db.session.commit()
    return jsonify(post_to_dict(post))


@api_bp.delete("/posts/<int:post_id>")
@login_required
def api_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.role != "admin" and post.author_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "deleted"})


@api_bp.get("/categories")
def api_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify([{"id": c.id, "name": c.name, "slug": c.slug} for c in categories])


@api_bp.post("/categories")
@login_required
def api_create_category():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    existing = Category.query.filter(db.func.lower(Category.name) == name.lower()).first()
    if existing:
        return jsonify({"error": "category already exists"}), 409
    category = Category(
        name=name, slug=unique_slug(Category, name), description=data.get("description", "")
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({"id": category.id, "name": category.name, "slug": category.slug}), 201


@api_bp.get("/tags")
def api_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return jsonify([{"id": t.id, "name": t.name, "slug": t.slug} for t in tags])


@api_bp.post("/comments")
def api_submit_comment():
    data = request.get_json(silent=True) or {}
    post_id = data.get("post_id")
    if not post_id:
        return jsonify({"error": "post_id required"}), 400
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "post not found"}), 404
    comment = Comment(
        body=(data.get("body") or "").strip(),
        author_name=(data.get("author_name") or "").strip(),
        author_email=(data.get("author_email") or "").strip(),
        post_id=post.id,
        approved=False,
    )
    if not comment.body or not comment.author_name or not comment.author_email:
        return jsonify({"error": "body, author_name, author_email are required"}), 400
    db.session.add(comment)
    db.session.commit()
    return jsonify({"message": "comment submitted for approval"}), 201


@api_bp.put("/comments/<int:comment_id>/approve")
@admin_only
def api_approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.approved = True
    db.session.commit()
    return jsonify({"message": "approved"})


@api_bp.delete("/comments/<int:comment_id>")
@admin_only
def api_delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "deleted"})
