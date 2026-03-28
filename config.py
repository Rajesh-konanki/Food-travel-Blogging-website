import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    MARVEL_YOUTUBE_URL = "https://www.youtube.com/@marvel"
    # Default Unsplash Images (free, no API key needed)
    DEFAULT_COVER = "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800"
    AVATAR_DEFAULT = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150"
    HERO_IMAGE = "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600"
    LOGO_IMAGE = "/static/images/logo.png"

    SAMPLE_POST_IMAGES = [
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
        "https://images.unsplash.com/photo-1526779259212-939e64788e3c?w=800",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=800",
        "https://images.unsplash.com/photo-1511988617509-a57c8a288659?w=800",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800",
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800",
        "https://images.unsplash.com/photo-1493612276216-ee3925520721?w=800",
        "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?w=800",
        "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800",
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800",
    ]

    CATEGORY_IMAGES = {
        "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600",
        "travel": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=600",
        "food": "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=600",
        "lifestyle": "https://images.unsplash.com/photo-1511988617509-a57c8a288659?w=600",
        "default": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=600",
    }

    AUTHOR_AVATARS = [
        "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100",
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100",
        "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=100",
        "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100",
        "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100",
    ]
    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    POSTS_PER_PAGE = 6
    WTF_CSRF_ENABLED = True
