import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def isPast(competition):
    competitionDate = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    return competitionDate < datetime.now()


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    matching_clubs = [club for club in clubs if club['email'] == email]
    if not matching_clubs:
        flash("Sorry, that email was not found.")
        return redirect(url_for('index'))
    club = matching_clubs[0]
    return render_template('welcome.html',club=club,competitions=competitions)



@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        if isPast(foundCompetition):
            flash('This competition is already over.')
            return render_template('welcome.html', club=foundClub, competitions=competitions)
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    flash("Something went wrong-please try again")
    return redirect(url_for('index'))

@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form.get('competition')), None)
    club = next((c for c in clubs if c['name'] == request.form.get('club')), None)
    if not competition or not club:
        flash("Something went wrong-please try again")
        return redirect(url_for('index'))
    if isPast(competition):
        flash('This competition is already over.')
        return render_template('welcome.html', club=club, competitions=competitions)
    try:
        placesRequired = int(request.form.get('places', ''))
    except ValueError:
        placesRequired = 0
    if placesRequired <= 0:
        flash('Please enter a valid number of places.')
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired > int(club['points']):
        flash('Not enough points to book that many places.')
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired > int(competition['numberOfPlaces']):
        flash('Not enough places available in this competition.')
        return render_template('welcome.html', club=club, competitions=competitions)
    booked = competition.setdefault('bookedPlaces', {})
    alreadyBooked = booked.get(club['name'], 0)
    if alreadyBooked + placesRequired > 12:
        flash('You cannot book more than 12 places in a competition.')
        return render_template('welcome.html', club=club, competitions=competitions)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    booked[club['name']] = alreadyBooked + placesRequired

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True) 