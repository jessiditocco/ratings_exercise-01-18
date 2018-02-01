"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

from correlation import pearson

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    # ratings = db.relationship('Rating')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} email={}>".format(self.user_id, self.email)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append((u_r.score, r.score))

        if paired_ratings:
            return pearson(paired_ratings)

        else:
            return 0.0


# Put your Movie and Rating model classes here.

class Movie(db.Model):
    """Movies in ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    released_at = db.Column(db.DateTime(), nullable=True)
    imdb_url = db.Column(db.String(200), nullable=True)

    # ratings = db.relationship('Rating')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id={} title={}>\n".format(self.movie_id, self.title)


class Rating(db.Model):
    """Ratings in ratings website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.ForeignKey("movies.movie_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)

    movie = db.relationship('Movie',
                            backref=db.backref('ratings',
                                               order_by=user_id))
    user = db.relationship('User',
                           backref=db.backref('ratings',
                                              order_by=user_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Rating rating_id={} movie_id={} user_id={} score={}>"
                .format(self.rating_id, self.movie_id, self.user_id, self.score))


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
