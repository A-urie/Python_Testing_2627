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