import json
from datetime import datetime

from flask import (
    Flask, flash, redirect, render_template, request, url_for
)

MAX_PLACES_PER_COMPETITION = 12


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def isPast(competition):
    competitionDate = datetime.strptime(
        competition['date'], '%Y-%m-%d %H:%M:%S'
    )
    return competitionDate < datetime.now()


def parsePlaces(value):
    try:
        places = int(value)
    except (TypeError, ValueError):
        return None
    if places <= 0:
        return None
    return places


def getPurchaseError(club, competition, placesRequired):
    if placesRequired > int(club['points']):
        return 'Not enough points to book that many places.'
    if placesRequired > int(competition['numberOfPlaces']):
        return 'Not enough places available in this competition.'
    alreadyBooked = competition.get('bookedPlaces', {}).get(club['name'], 0)
    if alreadyBooked + placesRequired > MAX_PLACES_PER_COMPETITION:
        return 'You cannot book more than 12 places in a competition.'
    return None


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    matching_clubs = [club for club in clubs if club['email'] == email]
    if not matching_clubs:
        flash("Sorry, that email was not found.", 'error')
        return redirect(url_for('index'))
    club = matching_clubs[0]
    return render_template(
        'welcome.html', club=club, competitions=competitions
    )


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition), None
    )
    if foundClub and foundCompetition:
        if isPast(foundCompetition):
            flash('This competition is already over.', 'error')
            return render_template(
                'welcome.html', club=foundClub, competitions=competitions
            )
        return render_template(
            'booking.html', club=foundClub, competition=foundCompetition
        )
    flash("Something went wrong-please try again", 'error')
    return redirect(url_for('index'))


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next(
        (c for c in competitions
         if c['name'] == request.form.get('competition')),
        None,
    )
    club = next(
        (c for c in clubs if c['name'] == request.form.get('club')),
        None,
    )
    if not competition or not club:
        flash("Something went wrong-please try again", 'error')
        return redirect(url_for('index'))
    if isPast(competition):
        flash('This competition is already over.', 'error')
        return render_template(
            'welcome.html', club=club, competitions=competitions
        )
    placesRequired = parsePlaces(request.form.get('places'))
    if placesRequired is None:
        flash('Please enter a valid number of places.', 'error')
        return render_template(
            'welcome.html', club=club, competitions=competitions
        )
    error = getPurchaseError(club, competition, placesRequired)
    if error:
        flash(error, 'error')
        return render_template(
            'welcome.html', club=club, competitions=competitions
        )
    booked = competition.setdefault('bookedPlaces', {})
    alreadyBooked = booked.get(club['name'], 0)
    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - placesRequired
    )
    club['points'] = int(club['points']) - placesRequired
    booked[club['name']] = alreadyBooked + placesRequired

    flash('Great-booking complete!', 'success')
    return render_template(
        'welcome.html', club=club, competitions=competitions
    )


@app.route('/pointsDisplay')
def pointsDisplay():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
