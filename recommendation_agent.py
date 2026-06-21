"""Recommendation agent for personalized sustainability actions."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from json_utils import parse_json_object
from llm_service import LLMService
from recommendation_prompt import build_recommendation_prompt


logger = logging.getLogger(__name__)


class RecommendationAgent:
    """Agent responsible only for creating sustainability recommendations.

    This agent receives carbon analysis and sustainability insight data, builds
    a recommendation prompt, sends it to the injected LLM service, and returns
    structured recommendations. It does not calculate emissions, generate
    challenges, or generate stories.
    """

    REQUIRED_RECOMMENDATION_KEYS = (
        "title",
        "description",
        "carbon_reduction_estimate",
        "cost_level",
        "effort_level",
        "priority_score",
        "reason",
    )

    def __init__(self, llm_service: Any) -> None:
        """Initialize the recommendation agent.

        Args:
            llm_service: Service object with a generate_response(prompt) method.
        """
        self.llm_service = llm_service

    def generate_recommendations(
        self,
        carbon_analysis: dict,
        sustainability_insights: dict,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate personalized recommendations from analysis and insights.

        Args:
            carbon_analysis: Structured output from CarbonAnalyzerAgent.
            sustainability_insights: Structured output from
                SustainabilityInsightAgent.

        Returns:
            A dictionary containing a recommendations list. Returns an empty
            recommendations list when generation, parsing, or validation fails.
        """
        if not isinstance(carbon_analysis, dict):
            logger.error(
                "Invalid carbon_analysis type: expected dict, got %s.",
                type(carbon_analysis).__name__,
            )
            return self._empty_response()

        if not isinstance(sustainability_insights, dict):
            logger.error(
                "Invalid sustainability_insights type: expected dict, got %s.",
                type(sustainability_insights).__name__,
            )
            return self._empty_response()

        try:
            prompt = build_recommendation_prompt(carbon_analysis, sustainability_insights)
            llm_response = self.llm_service.generate_response(prompt)

            if not llm_response:
                logger.error("LLM returned an empty recommendation response.")
                return self._empty_response()

            return self._parse_json_response(llm_response)

        except Exception as error:
            logger.exception("Recommendation generation failed: %s", error)
            return self._empty_response()

    def _parse_json_response(self, response: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse and validate the JSON recommendation response."""
        try:
            parsed_response = parse_json_object(response)
        except (ValueError, Exception) as error:
            logger.exception("Failed to parse recommendation JSON response: %s", error)
            return self._empty_response()

        recommendations = parsed_response.get("recommendations", [])
        if not isinstance(recommendations, list):
            logger.error("Invalid recommendation response: recommendations must be a list.")
            return self._empty_response()

        validated_recommendations = [
            self._validate_recommendation(item)
            for item in recommendations
            if isinstance(item, dict)
        ]

        if len(validated_recommendations) != len(recommendations):
            logger.warning("Some recommendation items were skipped because they were invalid.")

        return {"recommendations": validated_recommendations}

    def _validate_recommendation(self, recommendation: dict) -> Dict[str, Any]:
        """Validate one recommendation item and fill missing fields safely."""
        validated_item: Dict[str, Any] = {}

        for key in self.REQUIRED_RECOMMENDATION_KEYS:
            default_value: Any = 0 if key == "priority_score" else ""
            value = recommendation.get(key, default_value)

            if key == "priority_score" and not isinstance(value, (int, float)):
                logger.warning("Invalid priority_score value; using 0.")
                value = 0

            validated_item[key] = value

        return validated_item

    @staticmethod
    def _empty_response() -> Dict[str, List[Dict[str, Any]]]:
        """Return the default structured response for failed generation."""
        return {"recommendations": []}


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
    sustainability_insights_data = {
        "top_behaviors": ["Frequent solo car travel"],
        "root_causes": ["Most trips depend on a personal vehicle"],
        "opportunities": ["Short trips may be easier to replace with lower-carbon options"],
        "insights": ["Transportation choices are the main lifestyle pattern affecting emissions"],
    }

    recommendation_agent = RecommendationAgent(llm_service)
    recommendations = recommendation_agent.generate_recommendations(
        carbon_analysis_data,
        sustainability_insights_data,
    )
    print(recommendations)
