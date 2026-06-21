"""Utilities for parsing JSON responses from LLMs."""

from __future__ import annotations

import json
import re
from typing import Any, Dict


def parse_json_object(response: str) -> Dict[str, Any]:
    """Parse a JSON object from an LLM response.

    Args:
        response: Raw text returned by the LLM.

    Returns:
        Parsed JSON object as a dictionary.

    Raises:
        json.JSONDecodeError: If no valid JSON object can be parsed.
        ValueError: If the parsed JSON value is not an object.
    """
    cleaned_response = _remove_code_fences(response.strip())

    try:
        parsed_response = json.loads(cleaned_response)
    except json.JSONDecodeError:
        json_text = _extract_json_object_text(cleaned_response)
        parsed_response = json.loads(json_text)

    if not isinstance(parsed_response, dict):
        raise ValueError("Expected a JSON object.")

    return parsed_response


def _remove_code_fences(response: str) -> str:
    """Remove common markdown code fences from a response."""
    return re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        response,
        flags=re.IGNORECASE | re.MULTILINE,
    ).strip()


def _extract_json_object_text(response: str) -> str:
    """Extract the first top-level JSON object from mixed text."""
    start_index = response.find("{")
    end_index = response.rfind("}")

    if start_index == -1 or end_index == -1 or end_index <= start_index:
        raise json.JSONDecodeError("No JSON object found.", response, 0)

    return response[start_index : end_index + 1]
