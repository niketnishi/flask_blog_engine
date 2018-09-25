from flask import Flask, render_template, request, session, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required      # Maintains user session
from flaskblogengine.forms import RegistrationForm, LoginForm   # Importing registration and login classes from forms.py
from flaskblogengine.models import User, Post
from flaskblogengine import app, db, bcrypt
# from flask_session import Session

# Session(app)

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form_obj = RegistrationForm()
    if form_obj.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form_obj.password.data).decode('utf-8')
        user = User(username=form_obj.username.data, email=form_obj.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created', 'success')      # Flashes a message on submission
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form_obj)    # Passing registration object as form


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form_obj = LoginForm()
    if form_obj.validate_on_submit():
        user = User.query.filter_by(email=form_obj.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form_obj.password.data):
            login_user(user, remember=form_obj.remember.data)
            # Trying to access a page directly which needs login then it stores the url you are requesting and redirects to the page you are requesting after login.
            next_page = request.args.get('next')
        #     flash(f'You have logged in successfully!', 'success')      # Flashes a message on submission
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Incorrect Username or Password!', 'danger')
    return render_template('login.html', title='Login', form=form_obj)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required     # This decorator is used to prevent accessing page when trying to access account
def account():
    return render_template('account.html', title='Account')