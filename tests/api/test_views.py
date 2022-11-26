import os

import pytest

from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig


GET_RECO_PATH = "/reco/{model_name}/{user_id}"


GOOD_TOKEN = os.getenv('GOOD_API_TOKEN')
if GOOD_TOKEN is None:
    raise Exception('GOOD_TOKEN not in env variables.')

BAD_TOKEN = os.getenv('BAD_API_TOKEN')
if BAD_TOKEN is None:
    raise Exception('BAD_TOKEN not in env variables.')


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        headers = {"Authorization": f"Bearer {GOOD_TOKEN}"}
        response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        headers = {"Authorization": f"Bearer {GOOD_TOKEN}"}
        response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    user_id = 0
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    with client:
        headers = {"Authorization": f"Bearer {GOOD_TOKEN}"}
        response = client.get(path, headers=headers)
    assert response.status_code == 404


var_expect = [
    (GOOD_TOKEN, HTTPStatus.OK),
    (BAD_TOKEN, HTTPStatus.UNAUTHORIZED),
]
@pytest.mark.parametrize("var, expectation", var_expect)
def test_tokens(
    client: TestClient,
    var: str,
    expectation: HTTPStatus
) -> None:
    user_id = 0
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    print(f'var: {var}')
    print(f'expectation: {expectation}')
    with client:
        headers = {"Authorization": f"Bearer {var}"}
        response = client.get(path, headers=headers)
    assert response.status_code == expectation
