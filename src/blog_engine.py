from flask import Flask, render_template, request, session, url_for
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
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


if __name__ == '__main__':
    app.run(debug=True)
