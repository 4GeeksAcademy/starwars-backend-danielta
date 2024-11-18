from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    swapi_id = db.Column(db.Integer)
    url = db.Column(db.String(250))
    name = db.Column(db.String(50))
    birth_year = db.Column(db.String(40))
    gender = db.Column(db.String(20))
    height = db.Column(db.String(20))
    skin_color = db.Column(db.String(40))
    eye_color = db.Column(db.String(40))

    def __repr__(self):
        return '<Characters %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "swapi_id": self.swapi_id,
            "url": self.url,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    swapi_id = db.Column(db.Integer)
    url = db.Column(db.String(250))
    name = db.Column(db.String(50))
    climate = db.Column(db.String(40))
    population = db.Column(db.String(40))
    orbital_period = db.Column(db.String(50))
    rotation_period = db.Column(db.String(40))
    diameter = db.Column(db.String(50))

    def __repr__(self):
        return '<Planets %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "swapi_id": self.swapi_id,
            "url": self.url,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "diameter": self.diameter
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    user = db.relationship(User)
    character = db.relationship(Characters)
    planet = db.relationship(Planets)

    def __repr__(self):
        return '<Favorites %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
        }