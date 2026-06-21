"""Eco challenge agent for personalized sustainability habits."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Union

from challenge_prompt import build_challenge_prompt
from json_utils import parse_json_object
from llm_service import LLMService


logger = logging.getLogger(__name__)


class EcoChallengeAgent:
    """Agent responsible only for creating personalized eco challenges.

    This agent receives recommendation data, builds a challenge prompt, sends it
    to the injected LLM service, and returns structured challenge data. It does
    not calculate emissions, analyze behavior, generate recommendations, or
    generate stories.
    """

    REQUIRED_DAILY_CHALLENGE_KEYS = ("day", "task", "impact")

    def __init__(self, llm_service: Any) -> None:
        """Initialize the eco challenge agent.

        Args:
            llm_service: Service object with a generate_response(prompt) method.
        """
        self.llm_service = llm_service

    def generate_challenge(self, recommendations: dict) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """Generate a personalized eco challenge from recommendations.

        Args:
            recommendations: Structured recommendation data from
                RecommendationAgent.

        Returns:
            A dictionary containing a challenge name and daily challenges.
            Returns an empty structured response if generation, parsing, or
            validation fails.
        """
        if not isinstance(recommendations, dict):
            logger.error(
                "Invalid recommendations type: expected dict, got %s.",
                type(recommendations).__name__,
            )
            return self._empty_response()

        try:
            prompt = build_challenge_prompt(recommendations)
            llm_response = self.llm_service.generate_response(prompt)

            if not llm_response:
                logger.error("LLM returned an empty challenge response.")
                return self._empty_response()

            return self._parse_json_response(llm_response)

        except Exception as error:
            logger.exception("Eco challenge generation failed: %s", error)
            return self._empty_response()

    def _parse_json_response(self, response: str) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """Parse and validate the JSON challenge response."""
        try:
            parsed_response = parse_json_object(response)
        except (ValueError, Exception) as error:
            logger.exception("Failed to parse challenge JSON response: %s", error)
            return self._empty_response()

        challenge_name = parsed_response.get("challenge_name", "")
        if not isinstance(challenge_name, str):
            logger.warning("Invalid challenge_name value; using an empty string.")
            challenge_name = ""

        daily_challenges = parsed_response.get("daily_challenges", [])
        if not isinstance(daily_challenges, list):
            logger.error("Invalid challenge response: daily_challenges must be a list.")
            return self._empty_response()

        validated_daily_challenges = [
            self._validate_daily_challenge(item)
            for item in daily_challenges
            if isinstance(item, dict)
        ]

        if len(validated_daily_challenges) != len(daily_challenges):
            logger.warning("Some daily challenge items were skipped because they were invalid.")

        return {
            "challenge_name": challenge_name,
            "daily_challenges": validated_daily_challenges,
        }

    def _validate_daily_challenge(self, daily_challenge: dict) -> Dict[str, Any]:
        """Validate one daily challenge item and fill missing fields safely."""
        validated_item: Dict[str, Any] = {}

        for key in self.REQUIRED_DAILY_CHALLENGE_KEYS:
            default_value: Any = 1 if key == "day" else ""
            value = daily_challenge.get(key, default_value)

            if key == "day" and not isinstance(value, int):
                logger.warning("Invalid day value; using 1.")
                value = 1

            if key in {"task", "impact"} and not isinstance(value, str):
                logger.warning("Invalid %s value; using an empty string.", key)
                value = ""

            validated_item[key] = value

        return validated_item

    @staticmethod
    def _empty_response() -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """Return the default structured response for failed generation."""
        return {
            "challenge_name": "",
            "daily_challenges": [],
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    llm_service = LLMService()
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

    challenge_agent = EcoChallengeAgent(llm_service)
    challenge = challenge_agent.generate_challenge(recommendation_data)
    print(challenge)
