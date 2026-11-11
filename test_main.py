"""Regression tests for the local Flask/JWT workflow."""

import datetime
import json

import jwt
import pytest

import main


SECRET = "local-test-secret-at-least-32-bytes-long"
EMAIL = "wolf@thedoor.com"
PASSWORD = "huff-puff"


@pytest.fixture
def client(monkeypatch):
    # main reads its environment at import time, so patch the value it uses.
    monkeypatch.setattr(main, "JWT_SECRET", SECRET)
    monkeypatch.setitem(main.APP.config, "TESTING", True)
    return main.APP.test_client()


def test_health(client):
    assert False, "Intentional check: this commit must not deploy"
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == "Healthy"


def test_auth_and_contents_round_trip(client):
    response = client.post("/auth", json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 200
    token = response.json["token"]
    assert isinstance(token, str)

    claims = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert claims["email"] == EMAIL
    assert "password" not in claims
    assert claims["exp"] - claims["nbf"] == 14 * 24 * 60 * 60

    contents = client.get("/contents", headers={"Authorization": f"Bearer {token}"})
    assert contents.status_code == 200
    assert contents.json == claims


@pytest.mark.parametrize("field", ["email", "password"])
def test_auth_requires_fields(client, field):
    body = {"email": EMAIL, "password": PASSWORD}
    del body[field]
    response = client.post("/auth", json=body)
    assert response.status_code == 400
    assert response.json == {"message": f"Missing parameter: {field}"}


@pytest.mark.parametrize("body", [None, [], "not an object"])
def test_auth_rejects_non_object_json(client, body):
    response = client.post("/auth", data=json.dumps(body), content_type="application/json")
    assert response.status_code == 400


def test_contents_requires_authorization(client):
    assert client.get("/contents").status_code == 401


@pytest.mark.parametrize("kind", ["malformed", "wrong-signature", "expired"])
def test_contents_rejects_invalid_tokens(client, kind):
    now = datetime.datetime.now(datetime.UTC)
    if kind == "malformed":
        token = "not-a-jwt"
    else:
        expires = now - datetime.timedelta(seconds=1) if kind == "expired" else now + datetime.timedelta(minutes=5)
        key = "different-test-secret-at-least-32-bytes" if kind == "wrong-signature" else SECRET
        token = jwt.encode({"email": EMAIL, "nbf": now, "exp": expires}, key, algorithm="HS256")
    response = client.get("/contents", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
