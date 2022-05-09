from flask import Flask, render_template, request, session, make_response, jsonify, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
from validators import validate_user_data
from numpy import load
from flask_cors import CORS
# import shutil

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
app.debug = True
Session(app)
CORS(app)

GET_REC_ENV = os.environ.get("THREE_ONE_EIGHT_ENV")
if GET_REC_ENV == 'prod':
    app.debug = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("JAWSDB_URL")
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/three_one_eight_v2'

db = SQLAlchemy(app)

@app.before_first_request
def setup():
    db.create_all()
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class App(db.Model):
    __tablename__ = 'apps'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    app_type = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50))

    def __init__(self, name, app_type, color='#4285f4'):
        self.name = name
        self.app_type = app_type
        self.color = color
    
    def __repr__(self) -> str:
        return str(self.id) + " " + self.name

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    maintopic = db.Column(db.String(100))
    subtopics = db.Column(db.String(100))

    def __init__(self, title, author, publisher, maintopic, subtopics):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.maintopic = maintopic
        self.subtopics = subtopics

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(5), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    writer = db.Column(db.String(100), nullable=False)
    star = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    def __init__(self, title, genre, year, director, writer, star, country, company):
        self.title = title
        self.genre = genre
        self.year = year
        self.director = director
        self.writer = writer
        self.star = star
        self.country = country
        self.company = company

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    developer = db.Column(db.String(200), nullable=False)
    publisher = db.Column(db.String(200), nullable=False)
    platforms = db.Column(db.String(100), nullable=False)
    categories = db.Column(db.String(200), nullable=False)
    genres = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    def __init__(self, title, developer, publisher, platforms, categories, genres, price):
        self.title = title
        self.developer = developer
        self.publisher = publisher
        self.platforms = platforms
        self.categories = categories
        self.genres = genres
        self.price = price

class FavoriteBooks(db.Model):
    __tablename__ = 'fav_books'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    def __init__(self, user_id, book_id):
        self.user_id = user_id
        self.book_id = book_id

class FavoriteMovies(db.Model):
    __tablename__ = 'fav_movies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

    def __init__(self, user_id, movie_id):
        self.user_id = user_id
        self.movie_id = movie_id

class FavoriteGames(db.Model):
    __tablename__ = 'fav_games'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

###########################
########### API ###########
###########################
@app.route('/')
def home():
    return make_response({'home': 'HOME'}, 200)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        content = request.get_json(silent=True)
        username = content['username']
        email = content['email']
        password = content['password']
        password_confirm = content['password-confirm']
        # username = request.form['username']
        # email = request.form['email']
        # password = request.form['password']
        # password_confirm = request.form['password-confirm']
        validation_result = validate_user_data(db, User, username, email, password, password_confirm)
        if validation_result == '':
            data = User(username, email, password)
            db.session.add(data)
            db.session.commit()
            return custom_message({'id': data.id}, 200)
        return custom_message({'validation': validation_result}, 404)
    except Exception as e:
        return custom_message({'message': e}, 404)

@app.route('/login', methods=['POST'])
def login():
    try:
        content = request.get_json(silent=True)
        username = content['username']
        password = content['password']
        # username = request.form['username']
        # password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return custom_message({'id': user.id, 'username': user.username, 'email': user.email}, 200)
        else:
            return custom_message({'msg': 'Incorrect email or password'}, 404)

    except Exception as e:
        return custom_message(e, 404)

@app.route('/logout', methods=['GET'])
def logout():
    return custom_message('Logged out', 200)

@app.route('/apps/new', methods=['GET', 'POST'])
def new_app():
    if request.method == 'GET':
        return render_template('new-app.html')
    else:
        try:
            name = request.form['name']
            app_type = request.form['type']
            app_color = request.form['color'] if request.form['color'] else '#4285f4'
            the_app = App(name, app_type, app_color)
            db.session.add(the_app)
            db.session.commit()
            print('created app:', the_app)
            return custom_message({'id': the_app.id, 'name': the_app.name, 'type': the_app.app_type, 'color': the_app.color}, 200)
        except Exception as e:
            return custom_message({'message': e}, 404)

@app.route('/apps/update', methods=['GET', 'POST'])
def update_app():
    if request.method == 'GET':
        return render_template('update-app.html')
    else:
        app_color = request.form['color'] if request.form['color'] else '#4285f4'
        id = request.form['id']
        the_app = App.query.filter(App.id == id).first()
        if the_app:
            the_app.color = app_color
            db.session.commit()
            return custom_message({'id': the_app.id, 'name': the_app.name, 'type': the_app.app_type, 'color': the_app.color}, 200)
        else:
            return custom_message({'msg': f'App with {id} is not found.'}, 404)

@app.route('/apps/delete/<int:id>', methods=['GET'])
def delete_app(id):
    the_app = App.query.filter(App.id == id).first()
    if not the_app:
        return custom_message({'msg': f'App with id {id} is not found.'}, 404)
    else:
        App.query.filter(App.id == id).delete()
        db.session.commit()
        return custom_message({'msg': f'App with id {id} is deleted.'}, 200)

@app.route('/apps')
def get_apps():
    apps = App.query.all()
    apps_map = {}
    for cur_app in apps:
        res = {}
        res['id'] = cur_app.id
        res['name'] = cur_app.name
        res['type'] = cur_app.app_type
        res['color'] = cur_app.color
        apps_map[cur_app.id] = res
        # apps_map[cur_app.id] = cur_app.name
    return custom_message(apps_map, 200)

@app.route('/apps/<int:id>')
def get_app(id):
    the_app = App.query.filter(App.id == id).first()
    if the_app:
        return custom_message({'id': the_app.id, 'name': the_app.name, 'type': the_app.app_type, 'color': the_app.color}, 200)
    else:
        return custom_message({'msg': f'App with {id} is not found.'}, 404)

@app.route('/get-rec', methods=['POST'])
def get_reccomendations():
    content = request.get_json(silent=True)
    query = content['query']
    item_type = content['type']
    # query = request.form['query']
    # item_type = request.form['type']
    print('query:', query)
    print('item_type:', item_type)
    if item_type == 'book':
        print('book recom')
        book = Book.query.filter_by(title=query).first()
        if book:
            book_ids = get_recommended_item_ids(item_type, book.id)
            books = Book.query.filter(Book.id.in_(book_ids)).all()
            response = {}
            for book in books:
                response[book.id] = {
                    'title': book.title, 
                    'author': book.author,
                    'publisher': book.publisher,
                    'main-topic': book.maintopic,
                    'subtopics': book.subtopics
                }
            return response

    elif item_type == 'movie':
        print('movie recom')
        movie = Movie.query.filter_by(title=query).first()
        if movie:
            movie_ids = get_recommended_item_ids(item_type, movie.id)
            movies = Movie.query.filter(Movie.id.in_(movie_ids)).all()
            response = {}
            for movie in movies:
                response[movie.id] = {
                    'title': movie.title, 
                    'genre': movie.genre,
                    'year': movie.year,
                    'director': movie.director,
                    'writer': movie.writer,
                    'star': movie.star,
                    'country': movie.country,
                    'company': movie.company,
                }
            return response
    elif item_type == 'game':
        print('game recom')
        game = Game.query.filter_by(title=query).first()
        if game:
            game_ids = get_recommended_item_ids(item_type, game.id)
            games = Game.query.filter(Game.id.in_(game_ids)).all()
            response = {}
            for game in games:
                response[game.id] = {
                    'title': game.title, 
                    'developer': game.developer,
                    'publisher': game.publisher,
                    'platforms': game.platforms,
                    'categories': game.categories,
                    'genres': game.genres,
                    'price': game.price,
                }
            return response
    else:
        print('invalid type')
        return custom_message(f"Item type {item_type} is not a valid type Berke kardesim.", 404)

def get_recommended_item_ids(item_type, id, num_of_recs=5):
    if id and num_of_recs > 0:
        filename = f"transform_result_{id}.npz"
        row = load(os.path.abspath(f"./recs/{item_type}/" + filename))['arr_0']
        sim_scores = list(enumerate(row))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[0:num_of_recs+1]
        ids = [i[0] for i in sim_scores]
        return ids
    else:
        return []

@app.route('/toggle-fav', methods=['POST'])
def toggle_fav():
    content = request.get_json(silent=True)
    user_id = content['user-id']
    item_id = content['item-id']
    item_type = content['item-type']
    if item_type == 'book':
        faved_book = FavoriteBooks.query.filter_by(user_id=user_id, book_id=item_id).first()
        if faved_book:
            FavoriteBooks.query.filter_by(user_id=user_id, book_id=item_id).delete()
            msg = "Book has been removed from favorites."
        else:
            new_fav = FavoriteBooks(user_id, item_id)
            db.session.add(new_fav)
            msg = 'Book is added to favorites.'
    elif item_type == 'movie':
        faved_movie = FavoriteMovies.query.filter_by(user_id=user_id, movie_id=item_id).first()
        if faved_movie:
            FavoriteMovies.query.filter_by(user_id=user_id, movie_id=item_id).delete()
            msg = "Movie has been removed from favorites."
        else:
            new_fav = FavoriteMovies(user_id, item_id)
            db.session.add(new_fav)
            msg = 'Movie is added to favorites.'
    elif item_type == 'game':
        faved_game = FavoriteGames.query.filter_by(user_id=user_id, game_id=item_id).first()
        if faved_game:
            FavoriteGames.query.filter_by(user_id=user_id, game_id=item_id).delete()
            msg = "Game has been removed from favorites."
        else:
            new_fav = FavoriteGames(user_id, item_id)
            db.session.add(new_fav)
            msg = 'Game is added to favorites.'
    else:
        return custom_message(f"Item type {item_type} is not a valid type Berke kardesim.", 404)

    print(msg)
    db.session.commit()
    return custom_message(msg, 200)

@app.route('/favs/<int:id>')
def get_user_favorites(id):
    favorites = { 'book': get_fav_books(id), 'movie': get_fav_movies(id), 'game': get_fav_games(id) }
    return custom_message(favorites, 200)

def get_fav_books(user_id):
    result = []
    fav_book_ids = list(map(lambda x: x.book_id, FavoriteBooks.query.filter_by(user_id=user_id)))
    fav_books = Book.query.filter(Book.id.in_(fav_book_ids)).all()
    for book in fav_books:
        result.append({
                    'title': book.title, 
                    'author': book.author,
                    'publisher': book.publisher,
                    'main-topic': book.maintopic,
                    'subtopics': book.subtopics
                })
    return result

def get_fav_movies(user_id):
    result = []
    fav_movie_ids = list(map(lambda x: x.movie_id, FavoriteMovies.query.filter_by(user_id=user_id)))
    fav_movies = Movie.query.filter(Movie.id.in_(fav_movie_ids)).all()
    for movie in fav_movies:
        result.append({
                    'title': movie.title, 
                    'genre': movie.genre,
                    'year': movie.year,
                    'director': movie.director,
                    'writer': movie.writer,
                    'star': movie.star,
                    'country': movie.country,
                    'company': movie.company,
                })
    return result

def get_fav_games(user_id):
    result = []
    fav_game_ids = list(map(lambda x: x.game_id, FavoriteGames.query.filter_by(user_id=user_id)))
    fav_games = Game.query.filter(Game.id.in_(fav_game_ids)).all()
    for game in fav_games:
        result.append({
                    'title': game.title, 
                    'developer': game.developer,
                    'publisher': game.publisher,
                    'platforms': game.platforms,
                    'categories': game.categories,
                    'genres': game.genres,
                    'price': game.price,
                })
    return result

@app.route('/clear-favs')
def clear_favs():
    FavoriteBooks.query.delete()
    FavoriteMovies.query.delete()
    db.session.commit()
    return custom_message('Favorites data has been cleared.', 200)

def custom_message(message, status_code): 
    return make_response(jsonify(message), status_code)

if __name__ == '__main__':
    app.run()
