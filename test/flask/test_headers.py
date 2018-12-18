from unittest.mock import patch

import pytest

from thunderstorm.flask.headers import rewrite_path_with_header


@patch('thunderstorm.flask.headers.logger')
def test_deprecated_before_deadline(mock_logger, flask_app):
    resp = flask_app.test_client().get('/future')

    assert mock_logger.warning.called
    assert not mock_logger.error.called
    assert resp.headers['Warning'] == (
        '299 - "Deprecated route, '
        'will be maintained until 2050-05-05T00:00:00"'
    )


@patch('thunderstorm.flask.headers.logger')
def test_deprecated_after_deadline(mock_logger, flask_app):
    resp = flask_app.test_client().get('/past')

    assert not mock_logger.warning.called
    assert mock_logger.error.called
    assert resp.headers['Warning'] == (
        '299 - "Deprecated route, '
        'will be maintained until 2012-12-12T00:00:00"'
    )


@patch('thunderstorm.flask.headers.logger')
def test_deprecated_no_deadline(mock_logger, flask_app):
    resp = flask_app.test_client().get('/none')

    assert mock_logger.warning.called
    assert not mock_logger.error.called
    assert resp.headers['Warning'] == (
        '299 - "Deprecated route"'
    )


@pytest.mark.parametrize('path,header,new_path', [
    (  # chops common suffix
        '/api/v3/device/dc9c0e76-3d99-11e8-8752-33401e43ad3b?page=1&dude=true',
        'type=prefix; source=/api/v1/screen; target=/api/v3/screen',
        '/api/v1/device/dc9c0e76-3d99-11e8-8752-33401e43ad3b?page=1&dude=true',
    ),
    (
        '/api/v3/device/dc9c0e76-3d99-11e8-8752-33401e43ad3b',
        'type=prefix; source=/api/v1/screen; target=/api/v3/screen',
        '/api/v1/device/dc9c0e76-3d99-11e8-8752-33401e43ad3b',
    ),
    (
        '/api/v3/device/dc9c0e76-3d99-11e8-8752-33401e43ad3b?page=1',
        'type=prefix; source=/api/v1; target=/api/v3',
        '/api/v1/device/dc9c0e76-3d99-11e8-8752-33401e43ad3b?page=1',
    ),
    (
        '/foo/bar?page=1',
        'type=transparent; source=/other/invalid; target=invalid/foo',
        '/foo/bar?page=1',
    ),
    (
        '/foo/bar',
        'type=static; source=/other/source; target=invalid/foo',
        '/other/source'
    ),
    (
        '/foo/bar?page=1&dude=true',
        'type=static; source=/other/source; target=invalid/foo',
        '/other/source?page=1&dude=true'
    ),
    (
        '/foo/bar?page=1',
        'type=invalid',
        '/foo/bar?page=1',
    ),
    (
        '/foo/bar?page=1',
        'adnao',
        '/foo/bar?page=1',
    ),
    (
        '/foo/bar?page=1',
        'type=prefix',
        '/foo/bar?page=1',
    ),
    (
        '/foo/bar?page=1',
        'type=prefix; source=/other/source; target=/other/prefix',
        '/foo/bar?page=1',
    )
])
def test_rewrite_path_with_header(path, header, new_path):
    assert rewrite_path_with_header(path, header) == new_path
