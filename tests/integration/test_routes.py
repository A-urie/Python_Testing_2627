import pytest

import server

UNKNOWN_EMAIL = 'inconnu@example.com'
OLD_COMP = {
    'name': 'Old Comp',
    'date': '2020-01-01 10:00:00',
    'numberOfPlaces': '25',
}


def buy(client, places, competition='Test Comp', club='Test Club'):
    return client.post(
        '/purchasePlaces',
        data={'competition': competition, 'club': club, 'places': places},
        follow_redirects=True,
    )


def get(client, url):
    return client.get(url, follow_redirects=True)


def test_show_summary_with_known_email(client):
    email = server.clubs[0]['email']
    response = client.post('/showSummary', data={'email': email})
    assert response.status_code == 200


def test_show_summary_with_unknown_email_does_not_crash(client):
    response = client.post('/showSummary', data={'email': UNKNOWN_EMAIL})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_unknown_email_displays_error_message(client):
    response = client.post(
        '/showSummary',
        data={'email': UNKNOWN_EMAIL},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Sorry, that email was not found.' in response.data


def test_purchase_places_deducts_club_points(client, sample_data):
    clubs, competitions = sample_data
    buy(client, '3')
    assert int(clubs[0]['points']) == 7
    assert int(competitions[0]['numberOfPlaces']) == 22


def test_purchase_places_refused_when_not_enough_points(client, sample_data):
    clubs, competitions = sample_data
    response = buy(client, '11')
    assert response.status_code == 200
    assert b'Not enough points' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[0]['numberOfPlaces']) == 25


def test_purchase_more_than_12_places_refused(client, sample_data):
    clubs, competitions = sample_data
    clubs[0]['points'] = '20'
    response = buy(client, '13')
    assert response.status_code == 200
    assert b'more than 12' in response.data
    assert int(clubs[0]['points']) == 20
    assert int(competitions[0]['numberOfPlaces']) == 25


def test_purchase_cumulative_places_above_12_refused(client, sample_data):
    clubs, competitions = sample_data
    clubs[0]['points'] = '20'
    buy(client, '8')
    response = buy(client, '5')
    assert b'more than 12' in response.data
    assert int(clubs[0]['points']) == 12
    assert int(competitions[0]['numberOfPlaces']) == 17


def test_purchase_more_than_available_places_refused(client, sample_data):
    clubs, competitions = sample_data
    competitions[0]['numberOfPlaces'] = '5'
    response = buy(client, '6')
    assert response.status_code == 200
    assert b'Not enough places' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[0]['numberOfPlaces']) == 5


def test_book_unknown_competition_shows_error(client, sample_data):
    response = get(client, '/book/Inconnue/Test%20Club')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_book_unknown_club_shows_error(client, sample_data):
    response = get(client, '/book/Test%20Comp/Inconnu')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_purchase_unknown_competition_shows_error(client, sample_data):
    response = buy(client, '2', competition='Inconnue')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


def test_purchase_unknown_club_shows_error(client, sample_data):
    response = buy(client, '2', club='Inconnu')
    assert response.status_code == 200
    assert b'Something went wrong' in response.data


@pytest.mark.parametrize('places', ['', 'abc', '0', '-3'])
def test_purchase_invalid_places_shows_error(client, sample_data, places):
    clubs, competitions = sample_data
    response = buy(client, places)
    assert response.status_code == 200
    assert b'valid number of places' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[0]['numberOfPlaces']) == 25


def test_purchase_past_competition_refused(client, sample_data):
    clubs, competitions = sample_data
    competitions.append(dict(OLD_COMP))
    response = buy(client, '2', competition='Old Comp')
    assert response.status_code == 200
    assert b'already over' in response.data
    assert int(clubs[0]['points']) == 10
    assert int(competitions[1]['numberOfPlaces']) == 25


def test_book_past_competition_refused(client, sample_data):
    clubs, competitions = sample_data
    competitions.append(dict(OLD_COMP))
    response = get(client, '/book/Old%20Comp/Test%20Club')
    assert response.status_code == 200
    assert b'already over' in response.data


def test_points_board_is_public_and_lists_all_clubs(client, sample_data):
    clubs, competitions = sample_data
    clubs.append(
        {"name": "Other Club", "email": "other@club.co", "points": "5"}
    )
    response = client.get('/pointsDisplay')
    assert response.status_code == 200
    assert b'Test Club' in response.data
    assert b'Other Club' in response.data
    assert b'test@club.co' not in response.data


def test_book_valid_competition_shows_booking_page(client, sample_data):
    response = get(client, '/book/Test%20Comp/Test%20Club')
    assert response.status_code == 200
    assert b'Test Comp' in response.data
    assert b'Places available: 25' in response.data


def test_logout_redirects_to_home(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
