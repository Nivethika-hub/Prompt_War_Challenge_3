"""Carbon analyzer agent for structured carbon footprint analysis."""

from __future__ import annotations

import logging
from typing import Any, Dict

from carbon_prompt import build_carbon_analysis_prompt
from json_utils import parse_json_object


logger = logging.getLogger(__name__)


class CarbonAnalyzerAgent:
    """Agent responsible for carbon analysis orchestration.

    This agent builds the analysis prompt, sends it to the injected LLM service,
    parses the model response, and returns structured data. It does not contain
    prompt text or recommendation logic.
    """

    def __init__(self, llm_service: Any) -> None:
        """Initialize the carbon analyzer agent.

        Args:
            llm_service: Service object with a generate_response(prompt) method.
        """
        self.llm_service = llm_service

    def analyze(self, user_data: dict) -> Dict[str, Any]:
        """Analyze user lifestyle data and return structured carbon analysis.

        Args:
            user_data: User lifestyle data such as transportation, electricity,
                food, waste, and shopping habits.

        Returns:
            Parsed carbon analysis data as a dictionary. Returns a structured
            error dictionary if the LLM response cannot be generated or parsed.
        """
        if not isinstance(user_data, dict):
            logger.error("Invalid user_data type: expected dict, got %s.", type(user_data).__name__)
            return self._error_response("User data must be a dictionary.")

        try:
            prompt = build_carbon_analysis_prompt(user_data)
            llm_response = self.llm_service.generate_response(prompt)

            if not llm_response:
                logger.error("LLM returned an empty response.")
                return self._error_response("LLM returned an empty response.")

            return self._parse_json_response(llm_response)

        except Exception as error:
            logger.exception("Carbon analysis failed: %s", error)
            return self._error_response("Carbon analysis failed.")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate a JSON response from the LLM."""
        try:
            parsed_response = parse_json_object(response)
        except (ValueError, Exception) as error:
            logger.exception("Failed to parse LLM JSON response: %s", error)
            return self._error_response("LLM response was not valid JSON.")

        return parsed_response

    @staticmethod
    def _error_response(message: str) -> Dict[str, Any]:
        """Create a consistent structured error response."""
        return {
            "total_emissions": "",
            "largest_contributor": "",
            "category_breakdown": {},
            "top_contributors": [],
            "analysis": "",
            "error": message,
        }
