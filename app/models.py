from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

blockers = db.Table(
    'blockers',
    db.Column('blocker_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('blocked_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    topic = db.relationship('Newtopic', lazy='dynamic')
    replys = db.relationship('Reply', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    blocked = db.relationship(
        'User', secondary=blockers,
        primaryjoin=(blockers.c.blocker_id == id),
        secondaryjoin=(blockers.c.blocked_id == id),
        backref=db.backref('blockers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def block(self, user):
        if not self.is_blocked(user):
            self.blocked.append(user)

    def unblock(self, user):
        if self.is_blocked(user):
            self.blocked.remove(user)

    def is_blocked(self, user):
        return self.blocked.filter(
            blockers.c.blocked_id == user.id).count() > 0

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Newtopic(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tag = db.Column(db.String(20))
    post = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User')

    def __init__(self, topic, post, tag, user_id):
        self.topic = topic
        self.post = post
        self.tag = tag
        self.user_id = user_id


class Ads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)  # Actual data, needed for Download
    rendered_data = db.Column(db.Text, nullable=False)  # Data to render the pic in browser
    pic_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, id, name, data, user_id, rendered_data, pic_date):
        self.id = id
        self.name = name
        self.data = data
        self.user_id = user_id
        self.pic_date = pic_date
        self.rendered_data = rendered_data


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20))


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20))
    post = db.Column(db.String(140))
    name = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, post, name, user_id):
        self.post = post
        self.name = name
        self.user_id = user_id


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20))
    post = db.Column(db.String(140))
    pid = db.Column(db.Integer)

    def __init__(self, post, tag, pid):
        self.post = post
        self.tag = tag
        self.pid = pid
