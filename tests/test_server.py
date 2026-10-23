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