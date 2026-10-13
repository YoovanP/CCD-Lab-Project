import pytest
from pydantic import ValidationError
from app.config import Settings


@pytest.mark.parametrize("key,value", [
    ("max_input_chars", 0), ("max_input_tokens", 513),
    ("max_concurrent_inferences", 0), ("inference_threads", 0),
    ("inference_timeout_seconds", 0),
])
def test_invalid_settings_fail_fast(key, value):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{key: value})


def test_environment_overrides(monkeypatch):
    monkeypatch.setenv("MAX_INPUT_CHARS", "123")
    monkeypatch.setenv("MODEL_LOCAL_FILES_ONLY", "true")
    settings = Settings(_env_file=None)
    assert settings.max_input_chars == 123
    assert settings.model_local_files_only is True
