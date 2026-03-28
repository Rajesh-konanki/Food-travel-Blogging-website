from datetime import datetime, timezone

from flask_login import UserMixin

from extensions import db, login_manager

post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(
        db.String(500),
        nullable=True,
        default="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100",
    )
    role = db.Column(db.String(20), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    posts = db.relationship("Post", back_populates="author", lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    posts = db.relationship("Post", back_populates="category", lazy=True)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    posts = db.relationship("Post", secondary=post_tags, back_populates="tags")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500), default="")
    cover_image = db.Column(
        db.String(500),
        nullable=True,
        default="https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800",
    )
    status = db.Column(db.String(20), default="draft", nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    views = db.Column(db.Integer, default=0, nullable=False)

    author = db.relationship("User", back_populates="posts")
    category = db.relationship("Category", back_populates="posts")
    tags = db.relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = db.relationship(
        "Comment", back_populates="post", lazy=True, cascade="all, delete-orphan"
    )

    def refresh_excerpt(self):
        plain = (self.content or "").strip()
        self.excerpt = plain[:150] + ("..." if len(plain) > 150 else "")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(80), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    approved = db.Column(db.Boolean, default=False, nullable=False)

    post = db.relationship("Post", back_populates="comments")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
