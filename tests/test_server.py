import pytest

import server


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        yield client

@pytest.fixture
def sample_data(monkeypatch):
    clubs = [{"name": "Test Club", "email": "test@club.co", "points": "10"}]
    competitions = [
        {"name": "Test Comp", "date": "2030-01-01 10:00:00", "numberOfPlaces": "25"}
    ]
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)
    return clubs, competitions


def test_show_summary_with_known_email(client):
    email = server.clubs[0]['email']
    response = client.post('/showSummary', data={'email': email})
    assert response.status_code == 200


def test_show_summary_with_unknown_email_does_not_crash(client):
    response = client.post('/showSummary', data={'email': 'inconnu@example.com'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')

def test_unknown_email_displays_error_message(client):
    response = client.post(
        '/showSummary',
        data={'email': 'inconnu@example.com'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Sorry, that email was not found.' in response.data

def test_purchase_places_deducts_club_points(client, sample_data):
    clubs, competitions = sample_data
    client.post(
        '/purchasePlaces',
        data={'competition': 'Test Comp', 'club': 'Test Club', 'places': '3'},
    )
    assert int(clubs[0]['points']) == 7
    assert int(competitions[0]['numberOfPlaces']) == 22

def test_purchase_places_refused_when_not_enough_points(client, sample_data):
    clubs, competitions = sample_data
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Test Comp', 'club': 'Test Club', 'places': '11'},
    )
    assert response.status_code == 200
    assert b'Not enough points' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[0]['numberOfPlaces']) == 25

def test_purchase_more_than_12_places_refused(client, sample_data):
    clubs, competitions = sample_data
    clubs[0]['points'] = '20'
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Test Comp', 'club': 'Test Club', 'places': '13'},
    )
    assert response.status_code == 200
    assert b'more than 12' in response.data
    assert int(clubs[0]['points']) == 20
    assert int(competitions[0]['numberOfPlaces']) == 25


def test_purchase_cumulative_places_above_12_refused(client, sample_data):
    clubs, competitions = sample_data
    clubs[0]['points'] = '20'
    data = {'competition': 'Test Comp', 'club': 'Test Club', 'places': '8'}
    client.post('/purchasePlaces', data=data)
    data['places'] = '5'
    response = client.post('/purchasePlaces', data=data)
    assert b'more than 12' in response.data
    assert int(clubs[0]['points']) == 12
    assert int(competitions[0]['numberOfPlaces']) == 17

def test_purchase_more_than_available_places_refused(client, sample_data):
    clubs, competitions = sample_data
    competitions[0]['numberOfPlaces'] = '5'
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Test Comp', 'club': 'Test Club', 'places': '6'},
    )
    assert response.status_code == 200
    assert b'Not enough places' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[0]['numberOfPlaces']) == 5

def test_book_unknown_competition_shows_error(client, sample_data):
    response = client.get('/book/Inconnue/Test%20Club', follow_redirects=True)
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_unknown_club_shows_error(client, sample_data):
    response = client.get('/book/Test%20Comp/Inconnu', follow_redirects=True)
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_purchase_unknown_competition_shows_error(client, sample_data):
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Inconnue', 'club': 'Test Club', 'places': '2'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_purchase_unknown_club_shows_error(client, sample_data):
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Test Comp', 'club': 'Inconnu', 'places': '2'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Something went wrong' in response.data

@pytest.mark.parametrize('places', ['', 'abc', '0', '-3'])
def test_purchase_invalid_places_shows_error(client, sample_data, places):
    clubs, competitions = sample_data
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Test Comp', 'club': 'Test Club', 'places': places},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'valid number of places' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[0]['numberOfPlaces']) == 25

def test_purchase_past_competition_refused(client, sample_data):
    clubs, competitions = sample_data
    competitions.append(
        {'name': 'Old Comp', 'date': '2020-01-01 10:00:00', 'numberOfPlaces': '25'}
    )
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Old Comp', 'club': 'Test Club', 'places': '2'},
    )
    assert response.status_code == 200
    assert b'already over' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[1]['numberOfPlaces']) == 25


def test_book_past_competition_refused(client, sample_data):
    clubs, competitions = sample_data
    competitions.append(
        {'name': 'Old Comp', 'date': '2020-01-01 10:00:00', 'numberOfPlaces': '25'}
    )
    response = client.get('/book/Old%20Comp/Test%20Club')
    assert response.status_code == 200
    assert b'already over' in response.data

def test_points_board_is_public_and_lists_all_clubs(client, sample_data):
    clubs, competitions = sample_data
    clubs.append({"name": "Other Club", "email": "other@club.co", "points": "5"})
    response = client.get('/pointsDisplay')
    assert response.status_code == 200
    assert b'Test Club' in response.data
    assert b'Other Club' in response.data
    assert b'test@club.co' not in response.data

    
    