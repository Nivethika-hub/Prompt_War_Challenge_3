"""Prompt builder for sustainability storytelling."""

from __future__ import annotations

import json


def build_story_prompt(
    carbon_analysis: dict,
    recommendations: dict,
) -> str:
    """Build a prompt for an AI Sustainability Storyteller.

    Args:
        carbon_analysis: Structured carbon analysis report from
            CarbonAnalyzerAgent.
        recommendations: Personalized recommendations from RecommendationAgent.

    Returns:
        A prompt that asks the model to create a short, personalized,
        motivational sustainability story in plain text.
    """
    carbon_analysis_json = json.dumps(carbon_analysis, indent=2, ensure_ascii=False)
    recommendations_json = json.dumps(recommendations, indent=2, ensure_ascii=False)

    return f"""
You are an AI Sustainability Storyteller for a multi-agent sustainability app.

Use the carbon analysis report and personalized recommendations to write a short
sustainability story for the user. The story should feel positive,
inspirational, human, and motivating.

Carbon analysis report:
{carbon_analysis_json}

Personalized recommendations:
{recommendations_json}

Your tasks:
1. Explain the user's current environmental impact.
2. Explain what improvements are possible.
3. Describe the positive impact if the recommendations are followed.
4. Create a one-year sustainability vision.
5. Encourage progress rather than perfection.

Rules:
- Return plain text only.
- Maximum 200 words.
- Avoid guilt-based language.
- Focus on achievable improvements.
- Personalize the story using the provided user data.
- Do not include markdown formatting.
- Do not include a title unless it naturally fits the story.
""".strip()
