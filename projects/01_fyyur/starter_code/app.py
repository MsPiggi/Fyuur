#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import date 
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate= Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
  now = datetime.utcnow()
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True, nullable = False)
  name = db.Column(db.String)
  genres = db.Column(db.ARRAY(db.String))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(500))
  seeking_talent = db.Column(db.Boolean, default = False)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref = "venue", lazy = True) 

  def get_venue(self, city, state):
        return self.query.filter(self.city==city, self.state==state).all()
  

  def details(self):
    return {
      'id': self.id,
      'name': self.name,
    }
  
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True, nullable = False)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(500))
  seeking_venue  = db.Column(db.Boolean, default = True)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref = "artist", lazy = True) 

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True, nullable = False)
  start_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable = False) 
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable = False) 

  


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


def conver_to_dictionary(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct

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
  current_time = datetime.now()
  areas = Venue.query.distinct('city','state').all()
  data = []
  for area in areas:
    venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()

    record = {
      "city": area.city,
      "state": area.state,
      "venues": venues,
    }
    data.append(record)
    print(venues)
    print(data)
  return render_template('pages/venues.html', areas=data)


# 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_str = request.form.get('search_term')
  venue_query = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_str))).all()
  
  response= []
  response.append({
	"venue_count":len(venue_query),
	"data": venue_query
	})
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venues = Venue.query.filter_by(id=venue_id).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  data =  []

  for venue in venues: 
    data.append({
        "name":venue.name,
        "id":venue.id,
        "genre":venue.genres,
        "city":venue.city,
        "state":venue.state,
        "address":venue.address,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link":venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "upcoming_shows": upcoming_shows,
        "past_shows":past_shows,
        "upcoming_shows_count": len(upcoming_shows),
        "past_shows_count": len(past_shows)
      })

  return render_template('pages/show_venue.html', venues=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  data = request.form
  vname = data['name']
  vcity = data['city']
  vstate = data['state']
  vaddress = data['address']
  vphone = data['phone']
  vgenres = data['genres']
  vfb_link = data['facebook_link']
  
  try:
      db.session.add(Venue(
          city=vcity,
          state=vstate,
          name=vname,
          address=vaddress,
          phone=vphone,
          facebook_link=vfb_link,
          genres=vgenres,
          seeking_talent=False,
          website="",
          image_link=""
      ))
  
  except expression:
      error = true
  
  finally:
      if not error:
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
      else:
          flash('An error occurred. Venue ' + vname + ' could not be listed.')
          db.session.rollback()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      flash('Venue was successfully deleted!')
      db.session.close()
  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_str = request.form.get('search_term')
  artist_query = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_str))).all()
  
  response= []
  response.append({
	"artist_count":len(artist_query),
	"data": artist_query
	})
  return render_template('pages/search_artists.html', results=response, search_term=search_str)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artists = Artist.query.filter_by(id=artist_id).all()
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  data =  []

  for artist in artists: 
    data.append({
        "name":artist.name,
        "id":artist.id,
        "genre":artist.genres,
        "city":artist.city,
        "state":artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link":artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "upcoming_shows": upcoming_shows,
        "past_shows":past_shows,
        "upcoming_shows_count": len(upcoming_shows),
        "past_shows_count": len(past_shows)
      })
  
  return render_template('pages/show_artist.html', artists=data)


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
      Artist.query.filter_by(id=artist_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      flash('Artist was successfully deleted!')
      db.session.close()
  return redirect(url_for('artists', methods=['GET']))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artists = Artist.query.filter_by(id=artist_id).all()
  print(artists)
  form = ArtistForm(obj=artists)
  for artist in artists: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
  return render_template('forms/edit_artist.html', form=form, artists=artists)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  data = request.form
  
  aname = data['name']
  acity = data['city']
  astate = data['state']
  aphone = data['phone']
  agenres = data['genres']
  afb_link = data['facebook_link']
  
  try:
    print('edited')
    artist = Artist.query.get(artist_id)
    artist.name = aname
    artist.city = acity
    artist.state = astate
    artist.phone = aphone
    artist.genres = agenres
    artist.facebook_link  = afb_link

    db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
      flash('Artist ' + aname + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venues = Venue.query.filter_by(id=venue_id).all()
  form =VenueForm(obj=venues)
  for venue in venues: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
  return render_template('forms/edit_venue.html', form=form, venues=venues)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  data = request.form
  
  aname = data['name']
  acity = data['city']
  astate = data['state']
  aphone = data['phone']
  agenres = data['genres']
  afb_link = data['facebook_link']
  
  try:
    print('edited')
    venue = Venue.query.get(venue_id)
    venue.name = aname
    venue.city = acity
    venue.state = astate
    venue.phone = aphone
    venue.genres = agenres
    venue.facebook_link  = afb_link

    db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
      flash('Venue ' + aname + ' was successfully edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  data = request.form
  aname = data['name']
  acity = data['city']
  astate = data['state']
  aphone = data['phone']
  agenres = data['genres']
  afb_link = data['facebook_link']
  
  try:
      db.session.add(Artist(
          city=acity,
          state=astate,
          name=aname,
          phone=aphone,
          genres=agenres,
          seeking_venue=False,
          seeking_description="",
          website="",
          image_link="",
          facebook_link=""
      ))
  
  except expression:
      error = true
  
  finally:
      if not error:
          db.session.commit()
          flash('Artist ' + aname + ' was successfully listed!')
      else:
          flash('An error occurred. Artist ' + aname + ' could not be listed.')
          db.session.rollback()

  return render_template('pages/home.html')


#  Shows
#  ---------------------------------------------------------------

@app.route('/shows')
def shows():
  return render_template('pages/shows.html', shows=Show.query.all())

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  data = request.form
  sartist_id = data['artist_id']
  svenue_id = data['venue_id']
  sstart_time = data['start_time']

  
  try:
      db.session.add(Show(
          artist_id=sartist_id,
          venue_id=svenue_id,
          start_time=sstart_time,

      ))
  
  except expression:
      error = true
  
  finally:
      if not error:
          db.session.commit()
          flash('Show on then ' + sstart_time + ' was successfully listed!')
      else:
          flash('An error occurred. Show could not be listed.')
          db.session.rollback()
  
  return render_template('pages/home.html')

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


#----------------------------------------------------------------------------#
# Old Data
#----------------------------------------------------------------------------#

""" Aritst/ID
data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  } 




  Venue/ID
    data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  
  
  
  
    /Venues
    data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }] 
  
  
  
  
  Shows
    data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]"""