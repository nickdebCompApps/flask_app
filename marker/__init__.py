from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required
from twilio.rest import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c3ff6daffd3a6cb8b253a7c59d34d70c5e559e5800b77eb799433020eeb7b6f1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marker.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = '_failure_'
token = '05fe9bb64e06a1944968c57ef58a773a'
sid = 'AC6a87fa2c42bb36674fe93fcf38676745'
client = Client(sid, token)
UPLOAD_FOLDER = '/static/images/profile_pics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from marker import routes
