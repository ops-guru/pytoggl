from mock import Mock, patch
import pytest

from pytoggl.session import Session
from pytoggl.error import Error


@patch('pytoggl.session.requests')
def test_session_setup(requests):
    session = requests.Session.return_value
    session.headers = {}

    s = Session('http://example.com/', 'my-secret-token')

    requests.Session.assert_called_once_with()
    assert session.auth == ('my-secret-token', 'api_token')
    assert session.headers['content-type'] == 'application/json'
    assert s.session == session


@patch('pytoggl.session.requests')
def test_session_get_calls_requests_session_get(requests):
    session = requests.Session.return_value
    session.get.return_value = Mock(status_code=200)
    session.get.return_value.json.return_value = {}

    s = Session('http://example.com/', 'my-secret-token')
    resp = s.get('foo', bar=1, baz='x y')

    session.get.assert_called_once_with(
        'http://example.com/foo', params={
            'bar': 1,
            'baz': 'x y'
        })

    assert resp == {}


@patch('pytoggl.session.requests')
def test_session_get_throws_error_on_error_response(requests):
    session = requests.Session.return_value
    session.get.return_value = rv = Mock(status_code=400)
    rv.headers = {'content-type': 'application/json'}
    rv.json.return_value = {'message': 'invalid request'}

    s = Session('http://example.com/', 'my-secret-token')

    with pytest.raises(Error) as e:
        s.get('foo')

    assert e.value.status_code == 400
    assert e.value.message == 'invalid request'


@patch('pytoggl.session.requests')
def test_session_get_throws_error_on_requets_error(requests):
    session = requests.Session.return_value
    session.get.side_effect = Exception('oh noez!')

    s = Session('http://example.com/', 'my-secret-token')

    with pytest.raises(Error) as e:
        s.get('foo')

    assert e.value.status_code == 0
    assert e.value.message == 'oh noez!'


@patch('pytoggl.session.requests')
def test_session_get_throws_error_on_non_json_response(requests):
    session = requests.Session.return_value
    session.get.return_value = Mock(status_code=200)
    session.get.return_value.json.side_effect = Exception('not a json!')

    s = Session('http://example.com/', 'my-secret-token')

    with pytest.raises(Error) as e:
        s.get('foo')

    assert e.value.status_code == 0
    assert e.value.message == 'not a json!'


@patch('pytoggl.session.requests')
def test_session_post_sends_post_request(requests):
    session = requests.Session.return_value
    session.post.return_value = Mock(status_code=200)
    session.post.return_value.json.return_value = {}

    s = Session('http://example.com/', 'my-secret-token')
    resp = s.post('foo', {'bar': 'baz'})

    assert resp == {}

    session.post.assert_called_once_with(
        'http://example.com/foo', data='{"bar": "baz"}')
