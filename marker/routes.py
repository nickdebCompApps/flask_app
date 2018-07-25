from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required
import random, string, secrets, os
from marker.models import User, Bookmarks
from marker import app, bcrypt, db, client
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
import re
from validate_email import validate_email
from werkzeug.utils import secure_filename

extensions = set(['png', 'jpg', 'jpeg', 'gif'])
photos = UploadSet('photos', IMAGES)
app.config['UPLOAD_FOLDER'] = 'marker/static/images/bookmarkimages'
app.config['UPLOADED_PHOTOS_DEST'] = 'marker/static/images/profile_pics'
configure_uploads(app, photos)


@app.route('/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash(f'You have been logged out since you tried to access the login page')
        return redirect(url_for('logout'))
    if request.form:
        if request.form['email'] != None and request.form['password'] != None:
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user, remember=False)
                next_page = request.args.get('next')
                flash(f'You have been logged in!', '_success_')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash(f'Invalid user or password!', '_failure_')
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        flash(f'You have been logged out since you tried to access the signup page')
        return redirect(url_for('logout'))
    if request.form:
        validity = validateSignUp(request.form)
        if validity[0] == True:
            email = request.form['email']
            username = request.form['username']
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user = User(username = username.lower(), email = email.lower(), password = password)
            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash(f'Somethin went wrong!')
                return redirect(url_for('signup'))
            flash(f'You have been signed up!', '_success_')
            return redirect(url_for('login'))
        else:
            flash(validity[1])
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash(f'You have been logged out!', '_success_')
        return redirect(url_for('login'))
    flash(f'You must be logged in to do that', '_failure_')
    return redirect(url_for('login'))

@app.route('/add/<string:password>/<string:username>')
@login_required
def addbookmark(password, username):
    if password and username:
        bookmark  = Bookmarks(markerName = 'Name', markerLink = request.args.get('url'), userid = current_user.id, user = current_user)
        bookmark.fetch_image()
        db.session.add(bookmark)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/deletebookmark/<string:id>')
@login_required
def deletebookmark(id):
    if current_user:
        bookmark = Bookmarks.query.filter_by(id = id).first()
        if bookmark.userid == current_user.id:
            Bookmarks.query.filter_by(id = id).delete()
            db.session.commit()
    flash(f'Deleted')
    return redirect(url_for('home'))

@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        if request.method == 'POST' and 'pic' in request.files:
            uploadPhoto(request.files)
            return redirect(url_for('home'))
        elif request.method == 'POST' and request.form and 'bookmarkpic' in request.files:
            if request.form['title'] and request.form['link']:
                filename = uploadPhotoToBookmark(request.files)
                bookmark = Bookmarks(markerName = request.form['title'], markerLink = request.form['link'], markerPic = filename, userid = current_user.id, user = current_user )
                db.session.add(bookmark)
                db.session.commit()
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
    marklets = Bookmarks.query.filter_by(userid = current_user.id).all()
    return render_template('home.html', marklets = marklets)









# validators

def uploadPhoto(files):
    file = files['pic'].filename.split('.')
    file[0] = 'PROFILEPIC' + secrets.token_hex(24)
    files['pic'].filename = file[0] + '.' + file[1]
    filename = photos.save(files['pic'])
    current_user.profile_pic = str(filename)
    db.session.commit()
    flash(f'Your profile pic has been changed!', '_success_')

def uploadPhotoToBookmark(files):
    file = files['bookmarkpic'].filename.split('.')
    file[0] = 'BOOKMARKPIC' + secrets.token_hex(24)
    files['bookmarkpic'].filename = file[0] + '.' + file[1]
    filename = photos.save(files['bookmarkpic'])
    return filename





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
