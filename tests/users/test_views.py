from unittest import mock

import requests
from flask import url_for

from project.users import tasks
from project.users.models import User
from project.users.factories import UserFactory


def test_pytest_setup(client, db):
    # test view
    response = client.get('/users/form/')
    assert response.status_code == 200

    # test db
    user = User(username='test', email='test@example.com')
    db.session.add(user)
    db.session.commit()
    assert user.id


def test_view_with_eager_mode(client, db, config, monkeypatch):
    mock_requests_post = mock.MagicMock()
    monkeypatch.setattr(requests, 'post', mock_requests_post)

    config.update(CELERY_TASK_ALWAYS_EAGER=True)

    response = client.get(url_for('users.user_subscribe'))
    assert response.status_code == 200

    user_name = 'michaelyin'
    user_email = f'{user_name}@accordbox.com'
    response = client.post(url_for('users.user_subscribe'),
                           data={'email': user_email,
                                 'username': user_name},
                           )

    assert response.status_code == 200
    assert b'sent task to Celery successfully' in response.data

    mock_requests_post.assert_called_with(
        'https://httpbin.org/delay/5',
        data={'email': user_email}
    )

def test_user_subscribe_view(client, db, monkeypatch):
    user = user_factory.build()

    task_add_subscribe = mock.MagicMock(name="task_add_subscribe")
    task_add_subscribe.return_value = mock.MagicMock(task_id='task_id')
    monkeypatch.setattr(tasks.task_add_subscribe, 'delay', task_add_subscribe)

    response = client.get(url_for('users.user_subscribe'))
    assert response.status_code == 200

    response = client.post(url_for('users.user_subscribe'),
                           data={'email': user.email,
                                 'username': user.username},
                           )

    assert response.status_code == 200
    assert b'sent task to Celery successfully' in response.data

    # query from the db again
    user = User.query.filter_by(username=user.username).first()
    task_add_subscribe.assert_called_with(
        user.id
    )
def test_post_succeed(db, monkeypatch, user):
    mock_requests_post = mock.MagicMock()
    monkeypatch.setattr(requests, 'post', mock_requests_post)

    task_add_subscribe(user.id)

    mock_requests_post.assert_called_with(
        'https://httpbin.org/delay/5',
        data={'email': user.email}
    )


def test_exception(db, monkeypatch, user):
    mock_requests_post = mock.MagicMock()
    monkeypatch.setattr(requests, 'post', mock_requests_post)

    mock_task_add_subscribe_retry = mock.MagicMock()
    monkeypatch.setattr(task_add_subscribe, 'retry', mock_task_add_subscribe_retry)

    mock_task_add_subscribe_retry.side_effect = Retry()
    mock_requests_post.side_effect = Exception()

    with pytest.raises(Retry):
        task_add_subscribe(user.id)