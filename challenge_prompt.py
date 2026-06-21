"""Prompt builder for personalized eco habit challenges."""

from __future__ import annotations

import json


def build_challenge_prompt(recommendations: dict) -> str:
    """Build a prompt for an AI Eco Habit Coach.

    Args:
        recommendations: Personalized sustainability recommendations from
            RecommendationAgent.

    Returns:
        A prompt that asks the model to create a personalized 7-day eco
        challenge and return only valid JSON.
    """
    recommendations_json = json.dumps(recommendations, indent=2, ensure_ascii=False)

    return f"""
You are an AI Eco Habit Coach for a multi-agent sustainability app.

Use the personalized sustainability recommendations to create a realistic
7-day eco challenge. Convert the recommendations into small daily actions that
are easy to complete and take less than 15 minutes each.

Personalized recommendations:
{recommendations_json}

Your tasks:
1. Create a personalized 7-day eco challenge.
2. Convert recommendations into small daily actions.
3. Ensure each challenge can be completed in less than 15 minutes.
4. Focus on realistic behavior changes.
5. Keep challenges easy and motivating.

Rules:
- One challenge per day.
- Keep tasks simple.
- Avoid overwhelming users.
- Use positive language.
- Return JSON only.
- Do not include markdown.
- Do not include code fences.
- Do not include any text before or after the JSON.

Use exactly this JSON format:
{{
  "challenge_name": "",
  "daily_challenges": [
    {{
      "day": 1,
      "task": "",
      "impact": ""
    }}
  ]
}}
""".strip()
