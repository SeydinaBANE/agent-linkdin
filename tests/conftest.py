from types import SimpleNamespace
from typing import Any

import pytest


class FakeMessages:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.response_text)])


class FakeAnthropicClient:
    def __init__(self, response_text: str = "réponse du modèle") -> None:
        self.messages = FakeMessages(response_text)


@pytest.fixture
def fake_client() -> FakeAnthropicClient:
    return FakeAnthropicClient()
