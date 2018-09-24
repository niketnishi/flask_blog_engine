from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = '2f240087efc301fa2bfb4a64a3d97845'       # Used to prevent cookies from hacks
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from flaskblogengine import controllers     # import here since there may be a chance that it goes in to circular import
