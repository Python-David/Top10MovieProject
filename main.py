from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-10-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api_key = "5cde96c5a0ded746c4792718a89e20b6"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), unique=True, nullable=False)
    rating = db.Column(db.Float(250))
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(1000), unique=True)
    img_url = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return '<Book %r>' % self.title


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's "
                "sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to "
                "a jaw-dropping climax. ",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)


# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    list_of_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(list_of_movies)):
        list_of_movies[i].ranking = len(list_of_movies) - i

    db.session.commit()

    return render_template("index.html", movies=list_of_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_title = request.args.get("title")

    if form.validate_on_submit():
        movie_to_change = Movie.query.filter_by(title=movie_title).first()
        movie_to_change.rating = form.rating.data
        movie_to_change.review = form.review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie_title, form=form)


@app.route("/delete")
def delete():
    movie_title = request.args.get("title")
    movie_to_delete = Movie.query.filter_by(title=movie_title).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()

    if form.validate_on_submit():
        movie_to_add = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": api_key, "query": movie_to_add})
        data = response.json()["results"]

        return render_template("select.html", options=data)

    return render_template("add.html", form=form)


@app.route("/find")
def find():
    movie_id = int(request.args.get("id"))
    if movie_id:
        movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(movie_url, params={"api_key": api_key})
        data = response.json()

        movie_db_img_url = "https://image.tmdb.org/t/p/w500"

        new_user_movie = Movie(
            title=data["original_title"],
            img_url=f"{movie_db_img_url}{data['poster_path']}",
            year=data["release_date"].split("-")[0],
            description=data["overview"]
        )

        db.session.add(new_user_movie)
        db.session.commit()

    return redirect(url_for("edit", title=new_user_movie.title))


if __name__ == '__main__':
    app.run(debug=True)
