from datetime import datetime

from flask import Flask

from config import Config
from extensions import db, login_manager, migrate
from models import Category, Post, Tag
from utils import highlight_text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from routes.api import api_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_common_data():
        categories = Category.query.order_by(Category.name.asc()).all()
        popular_posts = (
            Post.query.filter_by(status="published").order_by(Post.views.desc()).limit(5).all()
        )
        tags = Tag.query.order_by(Tag.name.asc()).all()
        return {
            "nav_categories": categories,
            "popular_posts": popular_posts,
            "all_tags": tags,
            "marvel_youtube_url": app.config.get("MARVEL_YOUTUBE_URL", ""),
            "current_year": datetime.now().year,
            "config": Config,
        }

    @app.template_filter("highlight")
    def highlight_filter(value, term):
        return highlight_text(value, term)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
