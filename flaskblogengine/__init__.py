from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt     # Using it for encrypting password and saving to database for security
from flask_login import LoginManager    # Used to manage login and sessions
from elasticsearch import Elasticsearch


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = '2f240087efc301fa2bfb4a64a3d97845'       # Used to prevent cookies from hacks
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'      # For making the '@login_required' work here 'login' is the function name
login_manager.login_message_category = 'info'   # Sending the message category
es = Elasticsearch('http://localhost:5000')

from flaskblogengine import controllers     # import here since there may be a chance that it goes in to circular import
