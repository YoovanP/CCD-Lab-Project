from app.model_registry import SENTIMENT


def test_list_and_details(client):
    listed = client.get("/api/models").json()
    assert len(listed) == 1
    assert listed[0]["id"] == "sentiment"
    assert listed[0]["ready"] is True
    assert listed[0]["revision"] == SENTIMENT.revision
    assert client.get("/api/models/sentiment").json() == listed[0]


def test_unknown_model_details(client):
    response = client.get("/api/models/untrusted-model")
    assert response.status_code == 404
    assert response.json() == {"detail": "Unknown model"}


def test_unknown_inference_model_never_calls_predict(client, application, monkeypatch):
    def forbidden(_text):
        raise AssertionError("Unknown model must not call the inference backend")
    monkeypatch.setattr(application.state.models["sentiment"], "predict", forbidden)
    response = client.post("/api/inference", json={"model": "../../secret", "input": "hello"})
    assert response.status_code == 404
