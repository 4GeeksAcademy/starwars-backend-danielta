"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Planets, Characters
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


def get_favs (id):
    favorites = Favorites.query.filter_by(user_id=id)
    favorites = list(map(lambda x: x.serialize(), favorites))
    return favorites



# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/get/initial', methods=['GET'])
def initial():
    response = requests.get("https://swapi.dev/api/people")
    people = response.json()['results']

    if Characters.query.all() == None:
        for pers in people:
            char_id = pers['url'].split('/')[-2]
            char = Characters(name = pers['name'], swapi_id = char_id, url = pers['url'], birth_year = pers['birth_year'], gender = pers['gender'], height=pers['height'], skin_color=pers['skin_color'], eye_color=pers['eye_color'])
            db.session.add(char)
            db.session.commit()

        records = Characters.query.all()
        records = list(map(lambda x: x.serialize(), records))

        response1 = requests.get("https://swapi.dev/api/planets")
        planets = response1.json()['results']

    if Planets.query.all() == None:
        for planet in planets:
            planet_id = planet['url'].split('/')[-2]
            plan = Planets(name = planet['name'], swapi_id = planet_id, url = planet['url'], climate=planet['climate'], population=planet['population'], orbital_period=planet['orbital_period'], rotation_period=planet['rotation_period'], diameter=planet['diameter'])
            db.session.add(plan)
            db.session.commit()

        records1 = Planets.query.all()
        records1 = list(map(lambda x: x.serialize(), records1))

    lists = {
        "character_records": records,
        "planet_records": records1
    }

    print("lists: ", lists)
    return jsonify(lists)

@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = Characters.query.all()
    all_characters = list(map(lambda x: x.serialize(), all_characters))
    return all_characters

@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))
    return all_planets

@app.route('/characters/<int:character_id>', methods=['GET'])
def character_info(character_id):
    character = Characters.query.get(character_id)
    character = character.serialize()
    return jsonify(character)

@app.route('/planets/<int:planet_id>', methods=['GET'])
def planet_info(planet_id):
    planet = Planets.query.get(planet_id)
    planet = planet.serialize()
    return jsonify(planet)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), all_users))
    return all_users

@app.route('/users', methods=['POST'])
def handle_person():
    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'email' not in body:
        raise APIException('You need to specify the email', status_code=400)

    user1 = User(password = body['password'], email = body['email'])
    db.session.add(user1)
    db.session.commit()
    return "ok", 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user1 = User.query.get(id)
    db.session.delete(user1)
    db.session.commit()
    return "deleted", 200


@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_favorites(id):
    favorites = Favorites.query.filter_by(user_id=id)
    favorites = list(map(lambda x: x.serialize(), favorites))
    return jsonify(favorites)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):
    user_id = request.json['user_id']
    name = request.json['name']
    fav_planet = Favorites(name=name, user_id=user_id, planet_id=planet_id)
    db.session.add(fav_planet)
    db.session.commit()
    return jsonify(get_favs(user_id))

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_fav_character(character_id):
    user_id = request.json['user_id']
    name = request.json['name']
    fav_char = Favorites(name=name, user_id=user_id, character_id = character_id)
    db.session.add(fav_char)
    db.session.commit()
    return jsonify(get_favs(user_id))

@app.route('/favorite/planet/<int:user_id>/<int:favorite_id>', methods=['DELETE'])
def delete_fav_planet(favorite_id, user_id):
    fav_planet = Favorites.query.get(favorite_id)
    db.session.delete(fav_planet)
    db.session.commit()
    return jsonify(get_favs(user_id))

@app.route('/favorite/character/<int:user_id>/<int:favorite_id>', methods=['DELETE'])
def delete_fav_character(favorite_id, user_id):
    fav_char = Favorites.query.get(favorite_id)
    db.session.delete(fav_char)
    db.session.commit()
    return jsonify(get_favs(user_id))







# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
