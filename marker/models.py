from marker import db, login_manager
from flask_login import UserMixin
from selenium import webdriver
import os,secrets
from pyvirtualdisplay import Display

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'images/profile_pics')
MEDIA_URL = '/images/profile_pics'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    profile_pic = db.Column(db.String(128), nullable=False, default='default.jpg')

class Bookmarks(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    markerName = db.Column(db.String(14), nullable=False)
    markerPic = db.Column(db.String(128), nullable=False, default="defaultBookmark.jpg")
    markerLink = db.Column(db.String(128), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='usermarkers', lazy=True,  foreign_keys=[userid])

    def fetch_image(self):
        try:
            driver = webdriver.Chrome("C:/Users/Study/Desktop/chromedriver_win32/chromedriver")
            width = 1024
            height = 912
            driver.get(self.markerLink)
            driver.set_window_size(width, height)
            ROOT = 'C:/Users/Study/Desktop/bookmark app/marker/static/images/profile_pics'
            path_ = secrets.token_hex(24) + '.jpg'
            fullpath_ = os.path.join(ROOT, path_)
            screenshot = driver.save_screenshot(fullpath_)
            self.markerPic = path_
            self.markerName = driver.title
        except:
            self.markerName = 'Name'
            self.markerPic = 'defaultBookmark.jpg'
            driver.quit()

        finally:
            driver.quit()
