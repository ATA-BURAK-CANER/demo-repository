import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    db_path = os.path.join(app.instance_path, 'events.db')
    default_db_uri = f'sqlite:///{db_path}'
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', default_db_uri),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    # static version for cache-busting in development
    app.config['STATIC_VERSION'] = os.environ.get('STATIC_VERSION', '1.0')

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    from models import db
    db.init_app(app)

    # blueprints
    from views import main_bp
    from admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app


if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_ENV', '').lower() == 'development'
    # enable reloader in development so template/static changes show up
    app.run(host='0.0.0.0', port=5000, debug=debug)
