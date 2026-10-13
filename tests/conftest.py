"""Fast fault-injection tests plus a separate, mandatory real-model integration suite."""
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.inference import Prediction, SentimentModel
from app.main import create_app


class TestModel:
    """Test double used only to isolate lifecycle and API errors."""
    __test__ = False

    def __init__(self, _spec, _settings):
        self.ready = False
        self.loads = 0

    def load(self):
        self.loads += 1
        self.ready = True

    def predict(self, _text):
        return Prediction("positive", 0.8, 8, False)

    def close(self):
        self.ready = False


@pytest.fixture
def application():
    return create_app(Settings(_env_file=None), model_factory=TestModel)


@pytest.fixture
def client(application):
    with TestClient(application) as active:
        yield active


@pytest.fixture(scope="session")
def real_client():
    # Never skip or substitute a stub on download/model failure.
    application = create_app(Settings(_env_file=None), model_factory=SentimentModel)
    with TestClient(application) as active:
        assert active.get("/health/ready").status_code == 200, (
            "Real model failed to load. Run scripts/prepare_model.py --verify."
        )
        yield active
