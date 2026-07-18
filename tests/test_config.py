from pathlib import Path

import pytest

from agent_linkdin.config import load_settings


def test_load_settings_nominal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")

    settings = load_settings()

    assert settings.openrouter_api_key == "sk-or-test"
    assert settings.max_iterations == 2


def test_load_settings_missing_key_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        load_settings()
