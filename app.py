#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from models import *
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
from datetime import datetime

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
  response = []
  
  for venue in venue_list:
    venue_location = venue.state + venue.city
    venue_to_show = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter(Show.venue_id==venue.id, Show.start_time > todays_date).count()
    }

    if venue_location in locations:
      index_of_macthing_location = [i for i,_ in enumerate(response) if _['city'] == venue.city and _['state'] == venue.state][0]
      response[index_of_macthing_location]['venues'].append(venue_to_show)
    else:
      locations.append(venue_location)
      response.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [venue_to_show]
      })

  return render_template('pages/venues.html', areas=response)

#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  searched_venues = "%{}%".format(request.form['search_term'])
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

#  Show Venue By Id
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  todays_date = datetime.now()
  upcoming_shows = []
  past_shows = []

  for show in venue.shows:
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

#  GET Create Venue Form
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

#  POST Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['POST'])
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
      seeking_description = request.form['seeking_description'],
    )

    if request.form.get('seeking_talent'):
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    body['name'] = venue.name
    body['id'] = venue.id
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + body['name'] + ' could not be listed.')
    return redirect(url_for('create_venue_form'))
  else:
    flash('Venue ' + body['name'] + ' was successfully listed!')
    return redirect(url_for('show_venue', venue_id=body['id']))

#  DELETE Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  body = {}
  try:
    venue = Venue.query.get(venue_id)
    body['id'] = venue.id
    body['name'] = venue.name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + body['name'] + ' could not be deleted.')
    return redirect(url_for('show_venue', venue_id=body['id']))
  else:
    flash('Venue ' + body['name'] + ' was successfully deleted!')
    return render_template('pages/home.html')

#  GET Edit Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.state.default = venue.state
  form.genres.default = venue.genres
  form.seeking_talent.default = venue.seeking_talent
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  POST Edit Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  body = {}
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
    venue.seeking_description = request.form['seeking_description']

    if request.form.get('seeking_talent'):
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    body['name'] = venue.name
    body['id'] = venue.id
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + body['name'] + ' could not be Updates.')
    return redirect(url_for('edit_venue', venue_id=body['id']))
  else:
    flash('Venue was successfully updated!')
    return redirect(url_for('show_venue', venue_id=body['id']))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  response = Artist.query.with_entities(Artist.id, Artist.name).order_by('id')
  return render_template('pages/artists.html', artists=response)

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

#  Show Artist By ID
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  todays_date = datetime.now()
  upcoming_shows = []
  past_shows = []

  for show in artist.shows:
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

  response = {
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

  return render_template('pages/show_artist.html', artist=response)

#  GET Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.state.default = artist.state
  form.genres.default = artist.genres
  form.seeking_venue.default = artist.seeking_venue
  form.process()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

#  POST Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  body = {}
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']

    if request.form.get('seeking_venue'):
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False

    body['name'] = artist.name
    body['id'] = artist.id
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + body['name'] + ' could not be Updated.')
    return redirect(url_for('edit_artist', artist_id=body['id']))
  else:
    flash('Artist was successfully updated!')
    return redirect(url_for('show_artist', artist_id=body['id']))


#  GET Create Artist Form
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

#  POST Create Artist
#  ----------------------------------------------------------------
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
      seeking_description = request.form['seeking_description'],
    )

    if request.form.get('seeking_venue'):
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    
    body['name'] = artist.name
    body['id'] = artist.id
    db.session.add(artist)
    db.session.commit()
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
@app.route('/shows')
def shows():
  shows = Show.query.order_by(db.desc(Show.start_time)).all()
  response = []

  for show in shows:
    linked_artist = Artist.query.get(show.artist_id)
    linked_venue = Venue.query.get(show.venue_id)
    response.append({
      'venue_id': show.venue_id,
      'venue_name': linked_venue.name,
      'artist_id': show.artist_id,
      'artist_name': linked_artist.name,
      'artist_image_link': linked_artist.image_link,
      'start_time': show.start_time
    })

  return render_template('pages/shows.html', shows=response)

#  GET Create Show Form
#  ----------------------------------------------------------------
@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

#  POST Create Show Form
#  ----------------------------------------------------------------
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
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
