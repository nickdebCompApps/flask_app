from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, abort, g
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required
import random, string, secrets, os

from app.models import User
from app import app, bcrypt, db

from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
import re
from validate_email import validate_email
from werkzeug.utils import secure_filename



@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('home.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash(f'You have been logged out!', '_success_')
        return redirect(url_for('login'))
    flash(f'You must be logged in to do that', '_failure_')
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')









# validators

extensions = set(['png', 'jpg', 'jpeg', 'gif'])
photos = UploadSet('photos', IMAGES)
app.config['UPLOAD_FOLDER'] = 'app/static/images/bookmarkimages'
app.config['UPLOADED_PHOTOS_DEST'] = 'app/static/images/profile_pics'
configure_uploads(app, photos)

def uploadPhoto(files):
    file = files['pic'].filename.split('.')
    file[0] = 'PROFILEPIC' + secrets.token_hex(24)
    files['pic'].filename = file[0] + '.' + file[1]
    filename = photos.save(files['pic'])
    current_user.profile_pic = str(filename)
    db.session.commit()
    flash(f'Your profile pic has been changed!', '_success_')






def validateSignUp(form):
    if form is not None:
        email = form['email']
        username = form['username']
        password = form['password']

    if all(i is not '' for i in [email,username,password]):
        if validate_email(email) and validEmail(email):
            if validUsername(username) and len(username) > 2 and len(username) < 16:
                if validPassword(password):
                    return True, "success"
                else:
                    return False, "Invalid Password"
            else:
                return False, "Invalid Username"
        else:
            return False, "Invalid Email"
    else:
        return False, "Fill out all parts of form!"

    return False, "Something went wrong, please try again!"





#HELPERS

def validUsername(username):
    user = User.query.filter_by(username=username.lower()).first()
    if user is not None:
        message = 'That username is taken. Please choose a different one.'
        return False, message
    else:
        message = 'Success'
        return True, message

def validEmail(email):
    user = User.query.filter_by(email=email.lower()).first()
    if user is not None:
        message = 'That email is taken. Please choose a different one.'
        return False, message
    else:
        message = 'Success'
        return True, message

def validPassword(password):
    if len(password) < 6 and len(password) > 64:
        messsage = 'Password must be 6-64 characters'
        return False, message
    elif re.search(r"\s", password):
        message = 'Passwords cannot contain spaces'
        return False, message
    else:
        message = 'Success'
        return True, message
