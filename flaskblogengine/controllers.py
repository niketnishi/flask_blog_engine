from flask import Flask, render_template, request, session, url_for, flash, redirect
from flaskblogengine.forms import RegistrationForm, LoginForm   # Importing registration and login classes from forms.py
from flaskblogengine.models import User, Post
from flaskblogengine import app
from flask_session import Session

Session(app)

posts = [
    {
        'author': 'Niket Nishi',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'Sept 22, 2018'
    },
    {
        'author': 'Antony CS',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'Sept 23, 2018'
    }
]


@app.route("/")
def home():
    return render_template('home.html', blogs=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form_obj = RegistrationForm()
    if form_obj.validate_on_submit():
        flash(f'Account created for {form_obj.username.data}!', 'success')      # Flashes a message on submission
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form_obj)    # Passing registration object as form


@app.route("/login", methods=['GET', 'POST'])
def login():
    form_obj = LoginForm()
    if form_obj.validate_on_submit():
        if form_obj.email.data == 'niketnishi@gmail.com' and form_obj.password.data == 'password':
            flash(f'You have logged in successfully!', 'success')      # Flashes a message on submission
            return redirect(url_for('home'))
        else:
            flash('Incorrect Username or Password!', 'danger')
    return render_template('login.html', title='Login', form=form_obj)