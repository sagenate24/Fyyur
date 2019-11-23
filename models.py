from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  website = db.Column(db.String(120), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
  image_link = db.Column(db.String(500), nullable=True, default="https://icon-library.net/images/placeholder-image-icon/placeholder-image-icon-7.jpg")
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  shows = db.relationship('Show', backref='Venue', lazy='dynamic')

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  website = db.Column(db.String(120), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
  image_link = db.Column(db.String(500), nullable=True, default="https://icon-library.net/images/placeholder-image-icon/placeholder-image-icon-7.jpg")
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  shows = db.relationship('Show', backref='Artist', lazy='dynamic')

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'))
  start_time = db.Column(db.DateTime(), default=datetime.utcnow)
