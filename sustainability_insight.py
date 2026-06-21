"""Sustainability insight agent for analyzing carbon footprint reports."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from insight_prompt import build_insight_prompt
from json_utils import parse_json_object
from llm_service import LLMService


logger = logging.getLogger(__name__)


class SustainabilityInsightAgent:
    """Agent responsible only for generating sustainability insights.

    This agent receives structured carbon analysis data, builds an insight
    prompt, sends it to the injected LLM service, and returns parsed insight
    data. It does not calculate emissions, generate recommendations, create
    challenges, or produce motivational stories.
    """

    REQUIRED_KEYS = ("top_behaviors", "root_causes", "opportunities", "insights")

    def __init__(self, llm_service: Any) -> None:
        """Initialize the sustainability insight agent.

        Args:
            llm_service: Service object with a generate_response(prompt) method.
        """
        self.llm_service = llm_service

    def generate_insights(self, carbon_analysis: dict) -> Dict[str, List[str]]:
        """Generate structured sustainability insights from carbon analysis data.

        Args:
            carbon_analysis: Structured output from CarbonAnalyzerAgent.

        Returns:
            A dictionary with top behaviors, root causes, opportunities, and
            insights. Empty lists are returned when generation or parsing fails.
        """
        if not isinstance(carbon_analysis, dict):
            logger.error(
                "Invalid carbon_analysis type: expected dict, got %s.",
                type(carbon_analysis).__name__,
            )
            return self._empty_response()

        try:
            prompt = build_insight_prompt(carbon_analysis)
            llm_response = self.llm_service.generate_response(prompt)

            if not llm_response:
                logger.error("LLM returned an empty insight response.")
                return self._empty_response()

            return self._parse_json_response(llm_response)

        except Exception as error:
            logger.exception("Sustainability insight generation failed: %s", error)
            return self._empty_response()

    def _parse_json_response(self, response: str) -> Dict[str, List[str]]:
        """Parse and validate the JSON response returned by the LLM."""
        try:
            parsed_response = parse_json_object(response)
        except (ValueError, Exception) as error:
            logger.exception("Failed to parse insight JSON response: %s", error)
            return self._empty_response()

        validated_response = self._empty_response()
        for key in self.REQUIRED_KEYS:
            value = parsed_response.get(key, [])
            if not isinstance(value, list):
                logger.warning("Invalid value for '%s': expected list.", key)
                value = []

            validated_response[key] = value

        return validated_response

    @staticmethod
    def _empty_response() -> Dict[str, List[str]]:
        """Return the default structured response for failed insight generation."""
        return {
            "top_behaviors": [],
            "root_causes": [],
            "opportunities": [],
            "insights": [],
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    llm_service = LLMService()
    carbon_analysis_data = {
        "total_emissions": "8.5 tons CO2e per year",
        "largest_contributor": "Transportation",
        "category_breakdown": {
            "transportation": "4.1 tons CO2e",
            "electricity": "1.8 tons CO2e",
            "food": "1.5 tons CO2e",
            "waste": "0.4 tons CO2e",
            "shopping": "0.7 tons CO2e",
        },
        "top_contributors": ["Transportation", "Electricity", "Food"],
        "analysis": "Transportation is the largest source of emissions.",
    }

    insight_agent = SustainabilityInsightAgent(llm_service)
    insights = insight_agent.generate_insights(carbon_analysis_data)
    print(insights)
