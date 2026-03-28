import os
import re
import unicodedata
import uuid

from markupsafe import Markup
from sqlalchemy import func
from werkzeug.utils import secure_filename

from extensions import db
from models import Category, Post, Tag

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}


def slugify(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-") or "post"


def unique_slug(model, title_value, current_id=None):
    base = slugify(title_value)
    slug = base
    counter = 1
    while True:
        query = model.query.filter_by(slug=slug)
        if current_id:
            query = query.filter(model.id != current_id)
        if not query.first():
            return slug
        slug = f"{base}-{counter}"
        counter += 1


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_storage, upload_folder):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = secure_filename(file_storage.filename).rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, new_filename))
    return new_filename


def parse_tags(tag_string):
    names = [name.strip() for name in (tag_string or "").split(",") if name.strip()]
    tags = []
    for name in names:
        existing = Tag.query.filter(func.lower(Tag.name) == name.lower()).first()
        if existing:
            tags.append(existing)
            continue
        tag = Tag(name=name, slug=unique_slug(Tag, name))
        db.session.add(tag)
        tags.append(tag)
    return tags


def get_or_create_category(name, description=""):
    if not name:
        return None
    category = Category.query.filter(func.lower(Category.name) == name.lower()).first()
    if category:
        return category
    category = Category(name=name, slug=unique_slug(Category, name), description=description)
    db.session.add(category)
    return category


def highlight_text(text, term):
    if not text or not term:
        return text
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return Markup(pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text))


def post_to_dict(post):
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "excerpt": post.excerpt,
        "content": post.content,
        "cover_image": post.cover_image,
        "status": post.status,
        "views": post.views,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        "author": post.author.username if post.author else None,
        "category": post.category.name if post.category else None,
        "tags": [tag.name for tag in post.tags],
    }
