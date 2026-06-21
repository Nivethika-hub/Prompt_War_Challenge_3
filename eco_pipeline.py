"""Pipeline coordinator for the multi-agent sustainability platform."""

from __future__ import annotations

import logging
from typing import Any, Dict

from carbon_analyzer import CarbonAnalyzerAgent
from challenge_generator import EcoChallengeAgent
from llm_service import LLMService
from recommendation_agent import RecommendationAgent
from storyteller import SustainabilityStoryAgent
from sustainability_insight import SustainabilityInsightAgent


logger = logging.getLogger(__name__)


class EcoPipeline:
    """Coordinate all sustainability AI agents into one report.

    The pipeline only orchestrates agent execution. It does not contain prompt
    logic, carbon calculations, recommendation logic, challenge generation
    rules, or storytelling rules.
    """

    def __init__(
        self,
        carbon_agent: Any,
        insight_agent: Any,
        recommendation_agent: Any,
        challenge_agent: Any,
        story_agent: Any,
    ) -> None:
        """Initialize the eco pipeline with dependency-injected agents.

        Args:
            carbon_agent: Agent with an analyze(user_data) method.
            insight_agent: Agent with a generate_insights(carbon_analysis) method.
            recommendation_agent: Agent with a generate_recommendations(...) method.
            challenge_agent: Agent with a generate_challenge(recommendations) method.
            story_agent: Agent with a generate_story(carbon_analysis, recommendations) method.
        """
        self.carbon_agent = carbon_agent
        self.insight_agent = insight_agent
        self.recommendation_agent = recommendation_agent
        self.challenge_agent = challenge_agent
        self.story_agent = story_agent

    def generate_report(self, user_data: dict) -> Dict[str, Any]:
        """Generate a complete sustainability report from user lifestyle data.

        Args:
            user_data: User lifestyle data to analyze.

        Returns:
            A structured report containing analysis, insights, recommendations,
            challenge, and story outputs. Empty sections are returned if the
            pipeline fails.
        """
        if not isinstance(user_data, dict):
            logger.error("Invalid user_data type: expected dict, got %s.", type(user_data).__name__)
            return self._empty_report()

        try:
            logger.info("Generating carbon analysis.")
            analysis = self.carbon_agent.analyze(user_data)

            logger.info("Generating sustainability insights.")
            insights = self.insight_agent.generate_insights(analysis)

            logger.info("Generating sustainability recommendations.")
            recommendations = self.recommendation_agent.generate_recommendations(
                analysis,
                insights,
            )

            logger.info("Generating eco challenge.")
            challenge = self.challenge_agent.generate_challenge(recommendations)

            logger.info("Generating sustainability story.")
            story = self.story_agent.generate_story(analysis, recommendations)

            return {
                "analysis": analysis,
                "insights": insights,
                "recommendations": recommendations,
                "challenge": challenge,
                "story": story,
            }

        except Exception as error:
            logger.exception("Eco pipeline report generation failed: %s", error)
            return self._empty_report()

    @staticmethod
    def _empty_report() -> Dict[str, Any]:
        """Return the default structured report for failed pipeline execution."""
        return {
            "analysis": {},
            "insights": {},
            "recommendations": {},
            "challenge": {},
            "story": "",
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    llm_service = LLMService()

    carbon_agent = CarbonAnalyzerAgent(llm_service)
    insight_agent = SustainabilityInsightAgent(llm_service)
    recommendation_agent = RecommendationAgent(llm_service)
    challenge_agent = EcoChallengeAgent(llm_service)
    story_agent = SustainabilityStoryAgent(llm_service)

    pipeline = EcoPipeline(
        carbon_agent=carbon_agent,
        insight_agent=insight_agent,
        recommendation_agent=recommendation_agent,
        challenge_agent=challenge_agent,
        story_agent=story_agent,
    )

    sample_user_data = {
        "transportation": {
            "primary_mode": "car",
            "weekly_km": 120,
        },
        "electricity": {
            "monthly_kwh": 250,
        },
        "food": {
            "diet_type": "mixed",
            "meat_meals_per_week": 6,
        },
        "waste": {
            "recycles": True,
            "trash_bags_per_week": 2,
        },
        "shopping": {
            "new_items_per_month": 5,
        },
    }

    report = pipeline.generate_report(sample_user_data)
    print(report)
