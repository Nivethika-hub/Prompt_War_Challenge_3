"""Prompt builder for carbon footprint analysis agents."""

from __future__ import annotations

import json


def build_carbon_analysis_prompt(user_data: dict) -> str:
    """Build a detailed prompt for a Carbon Footprint Analyst AI.

    Args:
        user_data: User lifestyle data for transportation, electricity, food,
            waste, shopping, and any other available sustainability inputs.

    Returns:
        A prompt that instructs the model to analyze carbon emissions and return
        only valid JSON.
    """
    user_data_json = json.dumps(user_data, indent=2, ensure_ascii=False)

    return f"""
You are a Carbon Footprint Analyst AI for a multi-agent sustainability app.

Analyze the user's lifestyle data and estimate carbon emissions for each major
category. Use reasonable assumptions when exact values are missing, and keep the
explanation simple enough for a beginner to understand.

User data:
{user_data_json}

Analyze these categories:
1. Transportation habits
2. Electricity consumption
3. Food habits
4. Waste generation
5. Shopping habits

Your tasks:
- Estimate carbon emissions for each category.
- Identify the largest contributor.
- Rank categories by impact from highest emissions to lowest emissions.
- Provide a simple explanation of the user's carbon footprint.
- Use numeric values in category_breakdown, measured in estimated tons CO2e per year.

Return ONLY valid JSON.
Do not include markdown.
Do not include code fences.
Do not include any text before or after the JSON.

Use exactly this JSON format:
{{
  "total_emissions": "",
  "largest_contributor": "",
  "category_breakdown": {{
    "transportation": 0,
    "electricity": 0,
    "food": 0,
    "waste": 0,
    "shopping": 0
  }},
  "top_contributors": [],
  "analysis": ""
}}
""".strip()
