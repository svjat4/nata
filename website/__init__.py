from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from os import path
from werkzeug.security import generate_password_hash
import locale
import os
from flask_cors import CORS
import traceback

# Load environment variables
load_dotenv(path.join(path.dirname(__file__), '.env'))
locale.setlocale(locale.LC_TIME, "id_ID")

login_manager = LoginManager()
db = SQLAlchemy()

def create_app():
    global app
    app = Flask(__name__)   
    CORS(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
    app.config['MAX_CONTENT_PATH'] = os.environ.get('MAX_CONTENT_PATH') * 1024 * 1024
    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models.user import User, Room

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(str(id))
    
    # Register blueprints
    from .views.auth.auth import auth
    from .views.admin.index import admin
    from .views.mahasiswa.index import students
    from .views.dosen.wadek import wadek

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')
    app.register_blueprint(students, url_prefix='/')
    app.register_blueprint(wadek, url_prefix='/')

    # Register filters
    from .utils import filters

    app.jinja_env.filters['format_date'] = filters.format_date
    app.jinja_env.filters['date_range'] = filters.date_range
    app.jinja_env.filters['enum'] = filters.enum
    app.jinja_env.filters['comma_join'] = filters.comma_join
    app.jinja_env.filters['to_html'] = filters.to_html

    # Register global error handler
    app.register_error_handler(401, lambda error: { 'message': str(error) })
    app.register_error_handler(404, lambda error: { 'message': str(error) })
    app.register_error_handler(500, lambda error: { 'message': str(error) })

    def global_error_handler(error):
        traceback.print_exc()
        return { 'message': str(error) }

    app.register_error_handler(Exception, global_error_handler) 

    with app.app_context():
        db.create_all()
        default_db = User.query.all()
        default_room = Room.query.all()
        if not default_db:
            new_admin = User(username='ftti', password=generate_password_hash('admin', method='pbkdf2:sha256'), role='admin')
            db.session.add(new_admin)
            db.session.commit()

        if not default_room:
            new_room = Room(name='Tidak Meminjam Ruangan', capacity="50", status="-", default="False")
            db.session.add(new_room)
            db.session.commit()

    return app
