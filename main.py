import json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from forms import EditMovieForm, AddMovieForm
from dotenv import load_dotenv
import os
import requests


# LOAD ENVIRONMENT VARIABLES FROM .ENV FILE
def configure():
    load_dotenv()


configure()

IMG_PATH = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2'
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_ENDPOINT = 'https://api.themoviedb.org/3/search/movie'
film_dict = {
    'api_key': TMDB_API_KEY,
    'query': None
}

# CREATE APP
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///my-movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'


db.create_all()
Bootstrap(app)


@app.route("/")
def home():
    # all_movies = db.session.query(Movie).all()
    all_movies = db.session.query(Movie).order_by(desc(Movie.rating)).all()
    print(all_movies)

    return render_template("index.html", all_movies=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    # print(f'DEBUG 1: {request.method}')
    if request.args.get('id'):
        movie_id = request.args.get('id')
        movie = Movie.query.filter_by(id=movie_id).first()
        # create form
        form_edit = EditMovieForm(id=movie_id)
        # form_edit.review.data='HELLO Everybody'
        # TODO : Check if there is already a review, if yes pre-populate in the form, else leave empty
        if request.method == 'GET' and movie.review:
            form_edit.review.data = movie.review
        # db.session.close()
        if form_edit.validate_on_submit():  # POST
            if form_edit.submit.data:  # IF CLICK SUBMIT
                # Update A Record By PRIMARY KEY

                movie_to_update = Movie.query.get(movie_id)
                movie_to_update.review = form_edit.review.data
                movie_to_update.rating = form_edit.rating.data
                db.session.commit()

            return redirect(url_for('home'))

        return render_template('edit.html', form=form_edit, movie=movie)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/search', methods=['GET', 'POST'])
def search():
    form_add_movie = AddMovieForm()

    if form_add_movie.validate_on_submit():
        print(form_add_movie.new_movie.data)
        search_movie = form_add_movie.new_movie.data
        film_dict['query'] = search_movie
        response = requests.get(TMDB_ENDPOINT, params=film_dict)
        response.raise_for_status()
        data = response.json()
        print(data['results'])

        return redirect(url_for('select_movie', result=json.dumps(data['results'])))

    return render_template('add.html', form=form_add_movie)


@app.route('/select', methods=['GET', 'POST'])
def select_movie():
    # result = request.args.getlist('result', type=str)
    result = request.args.get('result')
    result = json.loads(result)
    return render_template('select.html', result=result)


@app.route('/add')
def add_movie():
    movie = request.args.get("movie")
    movie = json.loads(movie)

    title = movie['title']
    release_date = movie['release_date']
    dt = datetime.strptime(release_date, '%Y-%m-%d')
    release_year = dt.year
    description = movie['overview']
    rating = movie['vote_average']
    img_url = IMG_PATH + movie['poster_path']

    # CREATE A NEW RECORD
    new_movie = Movie(
        title=title,
        year=release_year,
        description=description,
        rating=rating,
        ranking=0,
        review='',
        img_url=img_url
    )
    print('SESSION ADD START')
    db.session.add(new_movie)
    print('SESSION ADD END')

    try:
        print('SESSION COMMIT START')
        db.session.commit()
        print('SESSION COMMIT END')
    except:
        print('SESSION ROLLBACK START')
        db.session.rollback()
        print('SESSION ROLLBACK END')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
