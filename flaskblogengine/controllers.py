import os
import secrets  # For creating a random key to save image file
from PIL import Image   # Resizing images using pillow module to save space on our filesystem
from flask import Flask, render_template, request, session, url_for, flash, redirect, abort, Response
from flask_login import login_user, current_user, logout_user, login_required      # Maintains user session
from flaskblogengine.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm   # Importing registration and login classes from forms.py
from flaskblogengine.models import User, Post
from flaskblogengine import app, db, bcrypt, es, celery
# from flask_session import Session

# Session(app)


@app.route("/")
def home():
    posts = Post.query.all()    # Returns list of all records of Post
    posts = posts[::-1]     # Reversing a list
    return render_template('home.html', blogs=posts)


@app.route("/search", methods=['GET'])
def search():
    search_txt = request.args.get('search')
    conf_submit = request.args.get('submit')
    if conf_submit == 'Submit':
        # Searching text in 'post_index' of elasticsearch
        search_list = es.search(index='post_index', doc_type='post_index',
                                body = {'query': {'multi_match': {'query': search_txt, 'fields': ['author', 'title', 'content']}}})['hits']['hits']

        # flash(search_list, 'danger')
        if search_list:
            flash(f"Search Result for '{search_txt}'", 'success')
            return render_template('search-result.html', title='Search Result', results=search_list)
        else:
            flash("Your Search Do Not Match Any of Our Records", 'info')
            return redirect(url_for('home'))
    else:
        flash("Please submit to get the results...", 'danger')
        return redirect(url_for('home'))


@celery.task
def download_blog(post_id):
    post = Post.query.get_or_404(post_id)
    blog_content = post.title + '\t\t' + 'By ' + post.author.username + ' ' + post.date_posted.strftime('%d-%m-%Y') + '\n\n' + post.content
    blog_name = post.title.lower().replace(' ', '_') + '.txt'
    return (blog_content, blog_name)


@app.route('/post/<int:post_id>/export')
def export(post_id):
    result = download_blog.delay(post_id)
    file_content, file_name = result.wait()
    return Response(file_content, mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename={}".format(file_name)})


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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)       # Creating hex token of 8 bytes
    _, f_ext = os.path.splitext(form_picture.filename)      # '_' is used to throw away an unused variable in python
    picture_fn = random_hex + f_ext     # creating file name with the given file extension
    picture_full_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    new_img = Image.open(form_picture)      # Using PIL module here
    new_img.thumbnail(output_size)      # Converting the image to 125 X 125px

    new_img.save(picture_full_path)     # Saving the new converted image
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required     # This decorator is used to prevent accessing page when trying to access account
def account():
    account_form = UpdateAccountForm()
    if account_form.validate_on_submit():       # On submission of account info form we update the database.
        if account_form.picture.data:
            picture_file = save_picture(account_form.picture.data)
            current_user.img_file = picture_file
        current_user.username = account_form.username.data
        current_user.email = account_form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':       # Writing default username and email in the account form
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.img_file)
    return render_template('account.html', title='Account', img_file=image_file, account_form=account_form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    new_blog_form = PostForm()
    if new_blog_form.validate_on_submit():
        post = Post(title=new_blog_form.title.data, content=new_blog_form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        es.index(index='post_index', doc_type='post_index', id=post.id, body={'author': post.author.username,
                                                                              'title': post.title,
                                                                              'content': post.content,
                                                                              'date_posted': post.date_posted.strftime('%d-%m-%Y')})
        flash('Your blog has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Blog', new_blog_obj=new_blog_form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog.html', tiltle=post.title, blog=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('You Blog has been updated and posted successfully.', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Blog', new_blog_obj=form, legend='Update Blog')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    es.delete(index='post_index', doc_type='post_index', id=post_id, ignore=['400', '404'])
    # es.indices.delete('post_index')   --> Delete the index completely
    db.session.delete(post)
    db.session.commit()
    flash('Your blog has been deleted from our records.')
    return redirect(url_for('home'))
