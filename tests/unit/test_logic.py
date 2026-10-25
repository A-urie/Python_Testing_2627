import json
from datetime import datetime, timedelta

import pytest

import server

POINTS_ERROR = 'Not enough points to book that many places.'
PLACES_ERROR = 'Not enough places available in this competition.'
MAX_ERROR = 'You cannot book more than 12 places in a competition.'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def make(points='10', places='25', booked=None, name='Club A'):
    club = {'name': name, 'points': points}
    competition = {'name': 'Comp', 'numberOfPlaces': places}
    if booked is not None:
        competition['bookedPlaces'] = booked
    return club, competition


@pytest.mark.parametrize('value, expected', [
    ('1', 1),
    ('5', 5),
    ('12', 12),
    ('13', 13),
    ('100', 100),
    (' 4 ', 4),
    ('+3', 3),
    ('007', 7),
    ('9999', 9999),
    ('\t5\n', 5),
])
def test_parse_places_valid(value, expected):
    assert server.parsePlaces(value) == expected


@pytest.mark.parametrize('value', [
    '', 'abc', '0', '-3', None, ' ', '2.5', '1e2', '1,5', '-0', '12abc',
])
def test_parse_places_invalid(value):
    assert server.parsePlaces(value) is None


@pytest.mark.parametrize('kwargs, requested, expected', [
    pytest.param(
        {}, 3, None, id='normal-purchase',
    ),
    pytest.param(
        {'points': '5'}, 5, None, id='spend-all-points',
    ),
    pytest.param(
        {'points': '20'}, 12, None, id='exactly-12-places',
    ),
    pytest.param(
        {'points': '4'}, 5, POINTS_ERROR, id='not-enough-points',
    ),
    pytest.param(
        {'places': '3'}, 4, PLACES_ERROR, id='not-enough-places',
    ),
    pytest.param(
        {'points': '20'}, 13, MAX_ERROR, id='13-places-at-once',
    ),
    pytest.param(
        {'points': '20', 'booked': {'Club A': 8}},
        5,
        MAX_ERROR,
        id='cumulative-above-12',
    ),
    pytest.param(
        {'points': '20', 'booked': {'Club A': 8}},
        4,
        None,
        id='cumulative-exactly-12',
    ),
    pytest.param(
        {'points': '20', 'booked': {'Other Club': 12}},
        5,
        None,
        id='other-club-bookings-ignored',
    ),
    pytest.param(
        {'points': '1', 'places': '0'},
        2,
        POINTS_ERROR,
        id='points-checked-first',
    ),
    pytest.param(
        {'points': 10, 'places': 25}, 3, None, id='integer-values',
    ),
    pytest.param(
        {'places': 0}, 1, PLACES_ERROR, id='no-places-left',
    ),
    pytest.param(
        {'booked': {}}, 3, None, id='empty-booking-record',
    ),
])
def test_get_purchase_error(kwargs, requested, expected):
    club, competition = make(**kwargs)
    assert server.getPurchaseError(club, competition, requested) == expected


@pytest.mark.parametrize('date, expected', [
    ('2020-01-01 10:00:00', True),
    ('2099-01-01 10:00:00', False),
])
def test_is_past_with_fixed_dates(date, expected):
    assert server.isPast({'date': date}) is expected


def test_is_past_yesterday():
    yesterday = datetime.now() - timedelta(days=1)
    competition = {'date': yesterday.strftime(DATE_FORMAT)}
    assert server.isPast(competition) is True


def test_is_past_tomorrow():
    tomorrow = datetime.now() + timedelta(days=1)
    competition = {'date': tomorrow.strftime(DATE_FORMAT)}
    assert server.isPast(competition) is False


def test_is_past_invalid_date_raises():
    with pytest.raises(ValueError):
        server.isPast({'date': 'not a date'})


def test_max_places_constant_is_12():
    assert server.MAX_PLACES_PER_COMPETITION == 12


def test_load_clubs_reads_json_file(tmp_path, monkeypatch):
    data = {"clubs": [{"name": "A", "email": "a@a.co", "points": "3"}]}
    (tmp_path / 'clubs.json').write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    assert server.loadClubs() == data['clubs']


def test_load_competitions_reads_json_file(tmp_path, monkeypatch):
    data = {
        "competitions": [
            {
                "name": "C",
                "date": "2030-01-01 10:00:00",
                "numberOfPlaces": "5",
            }
        ]
    }
    (tmp_path / 'competitions.json').write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    assert server.loadCompetitions() == data['competitions']
