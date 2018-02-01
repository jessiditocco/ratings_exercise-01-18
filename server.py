"""Movie Ratings."""

import datetime
from jinja2 import StrictUndefined

from flask import (flash, Flask, redirect, render_template, request, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Movie, User, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/users')
def get_users():
    """Show list of users."""

    users = User.query.all()

    return render_template('user_list.html', users=users)


@app.route('/users/<int:user_id>')
def get_user_info(user_id):
    """Show list of user information."""

    user = User.query.get(user_id)

    return render_template('user_info.html', user=user)


@app.route('/movies')
def get_movies():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template('movie_list.html', movies=movies)


@app.route('/movies/<int:movie_id>')
def get_movie_info(movie_id):
    """Show list of movie information."""

    movie = Movie.query.get(movie_id)

    return render_template('movie_info.html', movie=movie)


@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    """Rate a movie."""

    score = request.form.get("rating")
    movie_id = request.form.get("movie_id")
    user_id = session.get("user_id")
    timestamp = datetime.datetime.now()

    if "user_id" not in session:
        flash("Hey, you're not logged in!")
        return redirect("/login")

    rating = Rating.query.filter_by(movie_id=movie_id,
                                    user_id=user_id).first()
    if not rating:
        # Only add a rating if the user is logged in
        rating = Rating(movie_id=movie_id,
                        user_id=user_id,
                        score=score,
                        timestamp=timestamp)
    else:
        rating.score = score

    db.session.add(rating)
    db.session.commit()
    flash("Successfully rated movie.")

    return redirect("/movies/{}".format(movie_id))


@app.route('/register_user', methods=['POST'])
def register_user():
    """Registers new user."""

    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(email=email).count() == 0:
        # if no users exists with that email address, update db
        user = User(email=email, password=password)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

        # Once we're done, we should commit our work
        db.session.commit()

        # logs user in
        session['user_id'] = user.user_id

        flash("Created account for {} with password {}.".format(email, password))

        return redirect('/')

    else:
        # if there are users with this email address-flash a message to user
        flash("There is already a user with that email.")

        return redirect('/register')


@app.route('/register')
def show_registration():
    """Displays user registration form."""

    return render_template("register.html")


@app.route('/login', methods=['GET'])
def show_login():
    """Displays login form."""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_user():
    """Logs the user into their account.
        Sends the user to their user page if login succesful.
        Redirects user to login page if unsuccesful login."""

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        # use try; if there is exactly one user, execute code block
        # If not, skip to except
        user = User.query.filter_by(email=email, password=password).one()
            # if there is a user with this email/pword combination,
            # add user's id to the session
        session['user_id'] = user.user_id
        flash('Logged in successfully.')
        return redirect('/users/{}'.format(user.user_id))
    except:
        flash('Invalid email/password combination.')
        return redirect('/login')


@app.route('/logout')
def logout():
    """Logs user out."""

    if "user_id" in session:
        del session["user_id"]

    flash("Logged out.")
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
