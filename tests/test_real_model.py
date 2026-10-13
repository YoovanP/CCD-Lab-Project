"""Prove inference with the actual pinned model, not a test double."""
import pytest


@pytest.mark.integration
@pytest.mark.parametrize("text,expected", [
    ("I love this product. It is absolutely wonderful!", "positive"),
    ("I hate this product. It is terrible and disappointing.", "negative"),
])
def test_real_predictions(real_client, text, expected):
    response = real_client.post("/api/inference", json={"model": "sentiment", "input": text})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["prediction"] == expected
    assert 0.5 <= body["confidence"] <= 1
    assert body["processing_time_ms"] > 0
    assert 2 < body["tokens_processed"] <= 256
    assert body["truncated"] is False


@pytest.mark.integration
def test_real_token_truncation(real_client):
    response = real_client.post("/api/inference", json={
        "model": "sentiment", "input": "bad " * 400
    })
    assert response.status_code == 200
    assert response.json()["truncated"] is True
    assert response.json()["tokens_processed"] == 256


@pytest.mark.integration
def test_real_model_cpu_provider_and_timeout(real_client):
    model = real_client.app.state.models["sentiment"]
    assert model._session.get_providers() == ["CPUExecutionProvider"]
    previous = model.settings.inference_timeout_seconds
    try:
        model.settings.inference_timeout_seconds = 0.000001
        response = real_client.post("/api/inference", json={
            "model": "sentiment", "input": "wonderful " * 150
        })
        assert response.status_code == 504
    finally:
        model.settings.inference_timeout_seconds = previous
    assert real_client.post("/api/inference", json={
        "model": "sentiment", "input": "This is wonderful."
    }).status_code == 200
