# imports
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import abort
import json, datetime
import sqlite3

# app config/db configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'LD449VaAKb'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# loads users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# user table for users (id, username, password, email, userPosts (int))
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    userPosts = db.Column(db.Integer, default=0)

# post table for posts (id, user, date created, location, email)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), nullable=False, unique=False)
    created = db.Column(db.String(100), nullable=False, unique=False)
    location = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=False)

# class register form (takes username, password, and email parameters)
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    email = PasswordField(validators=[
                             InputRequired(), Length(min=10, max=40)], render_kw={"placeholder": "Email"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

# login form class (takes username, password and email)
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

# route for homepage
@app.route('/')
def home():
    return render_template('home.html')

# route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    form = LoginForm()
    if form.validate_on_submit():
        # validates the form
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

# route to dashboard (kind of like homepage)
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    posts = Post.query.all()
    return render_template('dashboard.html', user=user, posts=posts)

# route for 404 error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
# route to logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# route to register
@ app.route('/register', methods=['GET', 'POST'])
def register():
    # creates form
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# route to create a carpool post
@app.route('/createCarpool', methods=['GET', 'POST'])
@login_required
def createCarpool():
    if request.method == 'POST':
        location = request.form['location']
        # creates the new post and adds to the table
        new_post = Post(location=location, user=user.username, created=datetime.datetime.now(), email=user.email)
        db.session.add(new_post)
        db.session.commit()
        user.userPosts += 1
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('createPool.html', user=user)

# route to edit account information
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        User.username = username
        User.password = password
        User.email = email
        db.session.commit()

        return redirect(url_for('dashboard', user=user))

    return render_template('editAccount.html')
        
# route for about page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
