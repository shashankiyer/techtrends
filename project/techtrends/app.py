import logging
import sqlite3
import sys

from flask import (
    Flask,
    jsonify,
    json,
    render_template,
    request,
    url_for,
    redirect,
    flash,
)
from werkzeug.exceptions import abort

db_connection_count = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    db_connection_count += 1
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    connection.close()
    if post is not None and "title" in post.keys():
        app.logger.info(f"Accessed existing title {post['title']}")
    return post


# Define the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"


# Define the main route of the web application
@app.route("/")
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return render_template("index.html", posts=posts)


@app.route("/healthz")
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype="application/json",
    )
    return response


@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    all_post = connection.execute("SELECT * FROM posts")
    total_posts = len(all_post.fetchall())

    response = app.response_class(
        response=json.dumps(
            {
                "db_connection_count": db_connection_count,
                "post_count": total_posts,
            }
        ),
        status=200,
        mimetype="application/json",
    )
    return response


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info("Path not found. 404 Error")
        return render_template("404.html"), 404
    else:
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    app.logger.info("About Us. Read all about it")
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            connection = get_db_connection()
            connection.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            connection.commit()
            connection.close()

            app.logger.info(f"New article created. The title of the article is {title}")

            return redirect(url_for("index"))

    return render_template("create.html")


# start the application on port 3111
if __name__ == "__main__":
    stdout_logger = logging.StreamHandler(sys.stdout)
    stdout_logger.setLevel(logging.DEBUG)
    stdout_logger.setFormatter("%(asctime)s - %(levelname)s: %(message)s")
    app.logger.addHandler(stdout_logger)

    stderr_logger = logging.StreamHandler(sys.stderr)
    stderr_logger.setLevel(logging.ERROR)
    stderr_logger.setFormatter("%(asctime)s - %(levelname)s: %(message)s")
    app.logger.addHandler(stderr_logger)

    app.run(host="0.0.0.0", port="3111", debug=True)
