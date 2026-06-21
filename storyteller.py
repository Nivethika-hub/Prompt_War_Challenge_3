"""Sustainability story agent for personalized motivational stories."""

from __future__ import annotations

import logging
from typing import Any

from llm_service import LLMService
from story_prompt import build_story_prompt


logger = logging.getLogger(__name__)


class SustainabilityStoryAgent:
    """Agent responsible only for creating personalized sustainability stories.

    This agent receives carbon analysis and recommendation data, builds a
    storytelling prompt, sends it to the injected LLM service, and returns the
    plain-text story. It does not calculate emissions, generate insights,
    generate recommendations, or generate challenges.
    """

    def __init__(self, llm_service: Any) -> None:
        """Initialize the sustainability story agent.

        Args:
            llm_service: Service object with a generate_response(prompt) method.
        """
        self.llm_service = llm_service

    def generate_story(self, carbon_analysis: dict, recommendations: dict) -> str:
        """Generate a personalized motivational sustainability story.

        Args:
            carbon_analysis: Structured output from CarbonAnalyzerAgent.
            recommendations: Structured output from RecommendationAgent.

        Returns:
            A plain-text sustainability story. Returns an empty string if the
            story cannot be generated.
        """
        if not isinstance(carbon_analysis, dict):
            logger.error(
                "Invalid carbon_analysis type: expected dict, got %s.",
                type(carbon_analysis).__name__,
            )
            return ""

        if not isinstance(recommendations, dict):
            logger.error(
                "Invalid recommendations type: expected dict, got %s.",
                type(recommendations).__name__,
            )
            return ""

        try:
            prompt = build_story_prompt(carbon_analysis, recommendations)
            llm_response = self.llm_service.generate_response(prompt)

            if not llm_response:
                logger.error("LLM returned an empty story response.")
                return ""

            return llm_response.strip()

        except Exception as error:
            logger.exception("Sustainability story generation failed: %s", error)
            return ""


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
    recommendation_data = {
        "recommendations": [
            {
                "title": "Replace one short car trip",
                "description": "Walk or bike for one nearby errand this week.",
                "carbon_reduction_estimate": "Low to moderate",
                "cost_level": "Free",
                "effort_level": "Easy",
                "priority_score": 8,
                "reason": "Short car trips add avoidable transport emissions.",
            }
        ]
    }

    story_agent = SustainabilityStoryAgent(llm_service)
    story = story_agent.generate_story(carbon_analysis_data, recommendation_data)
    print(story)
