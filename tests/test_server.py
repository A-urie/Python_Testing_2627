import pytest

import server


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        yield client


def test_show_summary_with_known_email(client):
    email = server.clubs[0]['email']
    response = client.post('/showSummary', data={'email': email})
    assert response.status_code == 200


def test_show_summary_with_unknown_email_does_not_crash(client):
    response = client.post('/showSummary', data={'email': 'inconnu@example.com'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')