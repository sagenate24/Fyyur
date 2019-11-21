#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from datetime import datetime
import sys
# from flask_migrate import Migrate
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
  phone = db.Column(db.String(120), nullable=False)
  website = db.Column(db.String(120), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=False)
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
  image_link = db.Column(db.String(500), nullable=True, default="https://icon-library.net/images/placeholder-image-icon/placeholder-image-icon-7.jpg")
  genres = db.Column(db.ARRAY(db.String), nullable=True)

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  website = db.Column(db.String(120), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500), nullable=True)
  image_link = db.Column(db.String(500), nullable=True, default="https://icon-library.net/images/placeholder-image-icon/placeholder-image-icon-7.jpg")
  genres = db.Column(db.ARRAY(db.String), nullable=True)

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime(), default=datetime.utcnow)


  # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date_string = str(value)
  date = dateutil.parser.parse(date_string)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venue_list = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  todays_date = datetime.now()
  locations = []
  data = []
  
  for venue in venue_list:
    venue_location = venue.state + venue.city
    num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id, Show.start_time > todays_date).count()

    if venue_location in locations:
      index_of_macthing_location = [i for i,_ in enumerate(data) if _['city'] == venue.city and _['state'] == venue.state][0]
      data[index_of_macthing_location]['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': num_upcoming_shows
      })
    else:
      locations.append(venue_location)
      data.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [{
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_upcoming_shows
        }]
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form['search_term']
  searched_venues = "%{}%".format(search_term)
  venue_list = Venue.query.filter(Venue.name.ilike(searched_venues)).all()
  todays_date = datetime.now()

  response = {
    'count': len(venue_list),
    'data': []
  }

  for venue in venue_list:
    response['data'].append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter(Show.venue_id==venue.id, Show.start_time > todays_date).count()
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  shows = Show.query.with_entities(Show.artist_id, Show.start_time).filter_by(venue_id=venue_id).order_by('id').all()
  venue = Venue.query.get(venue_id)
  todays_date = datetime.now()
  upcoming_shows = []
  past_shows = []

  for show in shows:
    linked_artist = Artist.query.get(show.artist_id)
    current_show = {
      'artist_id': show.artist_id,
      'artist_name': linked_artist.name,
      'artist_image_link': linked_artist.image_link,
      'start_time': show.start_time
    }

    if todays_date > show.start_time:
      past_shows.append(current_show)
    else:
      upcoming_shows.append(current_show)

  response = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'address': venue.address,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST']) # DONEEEEEEEE ---
def create_venue_submission():
  error = False
  body = {}
  try:
    venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      website = request.form['website'],
      facebook_link = request.form['facebook_link'],
      seeking_talent = request.form['seeking_talent'] != None,
      seeking_description = request.form['seeking_description'],
    )

    db.session.add(venue)
    db.session.commit()
    body['name'] = venue.name
    body['id'] = venue.id
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + body['name'] + ' could not be listed.')
    return redirect(url_for('create_venue_form'))
  else:
    flash('Venue ' + body['name'] + ' was successfully listed!')
    return redirect(url_for('show_venue', venue_id=body['id']))

@app.route('/venues/<venue_id>', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  venue_name = 'unknown'
  try:
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + venue_name + ' could not be deleted.')
  else:
    flash('Venue ' + venue_name + ' was successfully deleted!')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name).order_by('id')
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form['search_term']
  searched_artist = "%{}%".format(search_term)
  artist_list = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(searched_artist)).all()
  todays_date = datetime.now()

  response = {
    'count': len(artist_list),
    'data': []
  }

  for artist in artist_list:
    response['data'].append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': Show.query.filter(Show.artist_id==artist.id, Show.start_time > todays_date).count()
    })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# --------- TODO show seeking performance venues ----------- #
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  shows = Show.query.with_entities(Show.venue_id, Show.start_time).filter_by(artist_id=artist_id).order_by('id').all()
  artist = Artist.query.get(artist_id)

  todays_date = datetime.now()
  upcoming_shows = []
  past_shows = []

  for show in shows:
    linked_venue = Venue.query.get(show.venue_id)
    current_show = {
      'venue_id': show.venue_id,
      'venue_name': linked_venue.name,
      'venue_image_link': linked_venue.image_link,
      'start_time': show.start_time
    }

    if todays_date > show.start_time:
      past_shows.append(current_show)
    else:
      upcoming_shows.append(current_show)

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.state.default = artist.state
  form.genres.default = artist.genres
  form.seeking_venue.default = artist.seeking_venue
  form.process()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  data = {}
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form['seeking_venue'] != None
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()

    data['name'] = artist.name
    data['id'] = artist.id
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close
  if error:
    flash('An error occurred. Artist ' + data['name'] + ' could not be Updates.')
    return redirect(url_for('edit_artist', artist_id=data['id']))
  else:
    flash('Artist was successfully updated!')
    return redirect(url_for('show_artist', artist_id=data['id']))

# --------- TODO: Need to set genres & state in the form ----------- #
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.state.default = venue.state
  form.genres.default = venue.genres
  form.seeking_talent.default = venue.seeking_talent
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  data = {}
  try:
    venue = Venue.query.get(venue_id)

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = request.form['seeking_talent'] != None
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()

    data['name'] = venue.name
    data['id'] = venue.id
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + data['name'] + ' could not be Updates.')
    return redirect(url_for('edit_venue', venue_id=data['id']))
  else:
    flash('Venue was successfully updated!')
    return redirect(url_for('show_venue', venue_id=data['id']))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  body = {}
  try:
    artist = Artist(
      name = request.form['name'],
      genres = request.form.getlist('genres'),
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      website = request.form['website'],
      facebook_link = request.form['facebook_link'],
      seeking_venue = request.form['seeking_venue'] != None,
      seeking_description = request.form['seeking_description'],
    )

    print(artist)

    db.session.add(artist)
    db.session.commit()
    body['name'] = artist.name
    body['id'] = artist.id
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + body['name'] + ' could not be listed.')
    return redirect(url_for('create_artist_form'))
  else:
    flash('Artist ' + body['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=body['id']))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows') # --------- TODO ----------- #
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/shows.html', shows=Show.query.all())

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# TODO: need to set artist/venue values link to primary tables
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = request.form['start_time']
    )

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
     db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    return redirect(url_for('create_shows'))
  else:
    flash('Show was successfully listed!')
  return redirect(url_for('shows'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
