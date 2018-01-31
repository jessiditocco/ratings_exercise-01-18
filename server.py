"""Movie Ratings."""

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
    """Logs the user into their account."""

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
        return redirect('/')
    except:
        flash('Invalid email/password combination.')
        return redirect('/login')



# @html.route('/users/<user_id>')
# def get_user_info():
#     """Show list of user information."""

#     user = User.query.get(user_id)

#     return render_template('user_list.html', users=users)


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
