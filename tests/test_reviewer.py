import json

from agent_linkdin.adapters.llm.reviewer import parse_review_response
from agent_linkdin.domain.models import Draft

DRAFT = Draft(content="Contenu du brouillon", iteration=0)


def test_parse_review_response_approved_with_polish() -> None:
    response = json.dumps(
        {"approved": True, "score": 9, "feedback": "", "improved_post": "Version polie"}
    )

    result = parse_review_response(response, DRAFT)

    assert result.approved
    assert result.final_post == "Version polie"


def test_parse_review_response_rejected_keeps_draft() -> None:
    response = json.dumps(
        {"approved": False, "score": 4, "feedback": "Hook trop faible", "improved_post": ""}
    )

    result = parse_review_response(response, DRAFT)

    assert not result.approved
    assert result.feedback == "Hook trop faible"
    assert result.final_post == DRAFT.content


def test_parse_review_response_markdown_fenced_json() -> None:
    response = '```json\n{"approved": true, "feedback": "", "improved_post": "Poli"}\n```'

    result = parse_review_response(response, DRAFT)

    assert result.approved
    assert result.final_post == "Poli"


def test_parse_review_response_invalid_json_auto_approves() -> None:
    result = parse_review_response("pas du JSON", DRAFT)

    assert result.approved
    assert result.final_post == DRAFT.content
