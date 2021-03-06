from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt     # Using it for encrypting password and saving to database for security
from flask_login import LoginManager    # Used to manage login and sessions
from elasticsearch import Elasticsearch
from celery import Celery

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = '2f240087efc301fa2bfb4a64a3d97845'       # Used to prevent cookies from hacks
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'

# Configure celery for background jobs
app.config['CELERY_BROKER_URL'] = 'amqp://'    # This URL tells Celery where the broker service is running
app.config['CELERY_RESULT_BACKEND'] = 'amqp://'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'      # For making the '@login_required' work here 'login' is the function name
login_manager.login_message_category = 'info'   # Sending the message category
es = Elasticsearch('http://localhost:9200')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])   # Running celery client with Flask application
celery.conf.update(app.config)

from flaskblogengine import controllers     # import here since there may be a chance that it goes in to circular import
