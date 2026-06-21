"""Streamlit dashboard for the AI-powered carbon footprint platform."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

import plotly.graph_objects as go
import streamlit as st

from carbon_analyzer import CarbonAnalyzerAgent
from challenge_generator import EcoChallengeAgent
from eco_pipeline import EcoPipeline
from llm_service import LLMService
from recommendation_agent import RecommendationAgent
from storyteller import SustainabilityStoryAgent
from sustainability_insight import SustainabilityInsightAgent


st.set_page_config(
    page_title="EcoMind Carbon Coach",
    page_icon="\U0001f331",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_custom_css() -> None:
    """Apply custom dashboard styling."""
    st.markdown(
        """
        <style>
            :root {
                --eco-primary: #15803d;
                --eco-secondary: #0f766e;
                --eco-soft: #ecfdf5;
                --eco-card: #ffffff;
                --eco-text: #10231a;
                --eco-muted: #5f6f66;
                --eco-border: #d9f2e4;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(187, 247, 208, 0.32), transparent 32rem),
                    linear-gradient(135deg, #f8fff9 0%, #f4fbf7 45%, #eefaf5 100%);
                color: var(--eco-text);
            }

            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1180px;
            }

            .hero {
                background: linear-gradient(135deg, #14532d 0%, #0f766e 100%);
                color: white;
                padding: 2.2rem;
                border-radius: 22px;
                box-shadow: 0 20px 45px rgba(15, 118, 110, 0.18);
                margin-bottom: 1.25rem;
            }

            .hero h1 {
                font-size: 2.45rem;
                line-height: 1.1;
                margin: 0 0 0.75rem 0;
                letter-spacing: 0;
            }

            .hero p {
                color: rgba(255, 255, 255, 0.88);
                font-size: 1.05rem;
                max-width: 760px;
                margin: 0;
            }

            [data-testid="stForm"],
            [data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(255, 255, 255, 0.94);
                border: 1px solid var(--eco-border);
                border-radius: 18px;
                box-shadow: 0 12px 30px rgba(21, 128, 61, 0.08);
            }

            [data-testid="stForm"] {
                padding: 1.25rem;
            }

            h1, h2, h3 {
                color: var(--eco-text);
                letter-spacing: 0;
            }

            [data-testid="stWidgetLabel"] p,
            [data-testid="stWidgetLabel"] div,
            .stSelectbox label, 
            .stNumberInput label, 
            .stSlider label {
                color: var(--eco-text) !important;
                font-weight: 600 !important;
            }

            .muted {
                color: var(--eco-muted);
                font-size: 0.95rem;
            }

            .pill {
                display: inline-block;
                background: var(--eco-soft);
                border: 1px solid var(--eco-border);
                color: var(--eco-primary);
                border-radius: 999px;
                padding: 0.35rem 0.7rem;
                font-weight: 700;
                margin: 0.15rem 0.25rem 0.15rem 0;
            }

            .recommendation {
                border-left: 4px solid var(--eco-primary);
                padding: 0.85rem 1rem;
                background: #fbfffc;
                border-radius: 12px;
                margin-bottom: 0.75rem;
            }

            .challenge-day {
                display: grid;
                grid-template-columns: 4.5rem minmax(0, 1fr);
                gap: 0.8rem;
                align-items: start;
                padding: 0.85rem;
                border: 1px solid var(--eco-border);
                border-radius: 14px;
                background: #ffffff;
                margin-bottom: 0.65rem;
            }

            .day-badge {
                background: #dcfce7;
                color: #166534;
                border-radius: 12px;
                text-align: center;
                padding: 0.5rem;
                font-weight: 800;
            }

            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid var(--eco-border);
                border-radius: 16px;
                padding: 1rem;
                box-shadow: 0 10px 24px rgba(21, 128, 61, 0.07);
            }

            .stButton > button,
            .stFormSubmitButton > button {
                background: linear-gradient(135deg, #16a34a, #0f766e);
                color: white;
                border: 0;
                border-radius: 14px;
                padding: 0.8rem 1.2rem;
                font-weight: 800;
                box-shadow: 0 12px 24px rgba(15, 118, 110, 0.18);
            }

            .stButton > button:hover,
            .stFormSubmitButton > button:hover {
                color: white;
                filter: brightness(1.03);
                border: 0;
            }

            @media (max-width: 768px) {
                .hero {
                    padding: 1.4rem;
                    border-radius: 18px;
                }

                .hero h1 {
                    font-size: 1.8rem;
                }

                .challenge-day {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def create_pipeline() -> EcoPipeline:
    """Create and cache the LLM service, agents, and pipeline."""
    llm_service = LLMService()

    return EcoPipeline(
        carbon_agent=CarbonAnalyzerAgent(llm_service),
        insight_agent=SustainabilityInsightAgent(llm_service),
        recommendation_agent=RecommendationAgent(llm_service),
        challenge_agent=EcoChallengeAgent(llm_service),
        story_agent=SustainabilityStoryAgent(llm_service),
    )


def render_hero() -> None:
    """Render the dashboard hero section."""
    st.markdown(
        """
        <div class="hero">
            <h1>EcoMind Carbon Coach</h1>
            <p>
                Turn everyday lifestyle choices into a clear carbon footprint report,
                practical recommendations, a 7-day challenge, and a motivating
                sustainability story.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def collect_user_data() -> Tuple[Dict[str, Any], bool]:
    """Render the main-page input form and return user data plus submit state."""
    st.header("Your Lifestyle Inputs")
    st.caption("Share approximate habits. Estimates are enough to get started.")

    with st.form("carbon_input_form"):
        transport_col, electricity_col = st.columns(2)

        with transport_col:
            st.subheader("Transportation habits")
            primary_transport = st.selectbox(
                "Primary transportation mode",
                ["Car", "Public transport", "Bike", "Walk", "Motorbike", "Work from home"],
                help="Choose the mode you use most often in a typical week.",
            )
            weekly_distance_km = st.number_input(
                "Weekly travel distance (km)",
                min_value=0.0,
                max_value=2000.0,
                value=80.0,
                step=5.0,
                help="Approximate total distance traveled each week.",
            )
            car_type = st.selectbox(
                "If you use a car, what type?",
                ["Not applicable", "Petrol", "Diesel", "Hybrid", "Electric"],
                help="This helps estimate transport emissions more accurately.",
            )

        with electricity_col:
            st.subheader("Electricity usage")
            monthly_kwh = st.number_input(
                "Monthly electricity usage (kWh)",
                min_value=0.0,
                max_value=5000.0,
                value=250.0,
                step=10.0,
                help="You can usually find this on your electricity bill.",
            )
            renewable_share = st.slider(
                "Renewable energy share (%)",
                min_value=0,
                max_value=100,
                value=10,
                help="Estimate how much electricity comes from renewable sources.",
            )

        food_col, waste_col, shopping_col = st.columns(3)

        with food_col:
            st.subheader("Food habits")
            diet_type = st.selectbox(
                "Diet style",
                ["Mixed diet", "Mostly vegetarian", "Vegetarian", "Vegan", "High meat"],
                help="Choose the option closest to your usual meals.",
            )
            meat_meals = st.number_input(
                "Meat-based meals per week",
                min_value=0,
                max_value=21,
                value=6,
                step=1,
                help="Count meals where meat is a main ingredient.",
            )
            food_waste = st.selectbox(
                "Food waste level",
                ["Low", "Medium", "High"],
                help="Estimate how often food is thrown away at home.",
            )

        with waste_col:
            st.subheader("Waste generation")
            trash_bags = st.number_input(
                "Trash bags per week",
                min_value=0,
                max_value=20,
                value=2,
                step=1,
                help="Approximate household trash bags produced weekly.",
            )
            recycling_frequency = st.selectbox(
                "Recycling frequency",
                ["Always", "Often", "Sometimes", "Rarely", "Never"],
                help="How often recyclable items are separated.",
            )

        with shopping_col:
            st.subheader("Shopping habits")
            new_items = st.number_input(
                "New non-food items per month",
                min_value=0,
                max_value=100,
                value=5,
                step=1,
                help="Clothes, electronics, home goods, and other purchased items.",
            )
            shopping_style = st.selectbox(
                "Shopping style",
                ["Only when needed", "Occasional", "Frequent", "Second-hand focused"],
                help="Choose the option closest to your buying habits.",
            )

        submitted = st.form_submit_button(
            "Analyze My Carbon Footprint",
            type="primary",
            use_container_width=True,
        )

    user_data = {
        "transportation": {
            "primary_mode": primary_transport,
            "weekly_distance_km": weekly_distance_km,
            "car_type": car_type,
        },
        "electricity": {
            "monthly_kwh": monthly_kwh,
            "renewable_energy_share_percent": renewable_share,
        },
        "food": {
            "diet_type": diet_type,
            "meat_meals_per_week": meat_meals,
            "food_waste_level": food_waste,
        },
        "waste": {
            "trash_bags_per_week": trash_bags,
            "recycling_frequency": recycling_frequency,
        },
        "shopping": {
            "new_items_per_month": new_items,
            "shopping_style": shopping_style,
        },
    }

    return user_data, submitted


def extract_number(value: Any) -> float:
    """Extract the first numeric value from a string or number."""
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return 0.0

    match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group()) if match else 0.0


def build_breakdown_chart(category_breakdown: Dict[str, Any]) -> go.Figure:
    """Build a Plotly pie chart for the emission breakdown."""
    labels: List[str] = []
    values: List[float] = []

    for category, emission in category_breakdown.items():
        value = extract_number(emission)
        if value > 0:
            labels.append(str(category).replace("_", " ").title())
            values.append(value)

    if not values:
        labels = ["Transportation", "Electricity", "Food", "Waste", "Shopping"]
        values = [1, 1, 1, 1, 1]

    figure = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.48,
                marker={
                    "colors": ["#15803d", "#0f766e", "#84cc16", "#22c55e", "#65a30d"],
                    "line": {"color": "#ffffff", "width": 3},
                },
                textinfo="label+percent",
            )
        ]
    )
    figure.update_layout(
        margin={"t": 20, "b": 20, "l": 20, "r": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend={"orientation": "h", "y": -0.08},
        height=420,
    )
    return figure


def render_metric_row(analysis: Dict[str, Any], recommendations: Dict[str, Any], challenge: Dict[str, Any]) -> None:
    """Render key report metrics."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Emissions", str(analysis.get("total_emissions", "Not available")))
    col2.metric("Largest Contributor", str(analysis.get("largest_contributor", "Not available")))
    col3.metric("Recommendations", len(recommendations.get("recommendations", [])))
    col4.metric("Eco Challenge", f'{len(challenge.get("daily_challenges", []))} days')


def render_list(items: List[Any], empty_text: str) -> None:
    """Render a clean bullet list from values."""
    if not items:
        st.caption(empty_text)
        return

    for item in items:
        st.markdown(f"- {item}")


def render_recommendations(recommendations: Dict[str, Any]) -> None:
    """Render personalized recommendations."""
    items = recommendations.get("recommendations", [])
    if not items:
        st.caption("No recommendations were generated.")
        return

    for index, item in enumerate(items, start=1):
        st.markdown(
            f"""
            <div class="recommendation">
                <strong>{index}. {item.get("title", "Recommendation")}</strong>
                <p>{item.get("description", "")}</p>
                <span class="pill">Impact: {item.get("carbon_reduction_estimate", "N/A")}</span>
                <span class="pill">Cost: {item.get("cost_level", "N/A")}</span>
                <span class="pill">Effort: {item.get("effort_level", "N/A")}</span>
                <span class="pill">Priority: {item.get("priority_score", 0)}</span>
                <p class="muted">{item.get("reason", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_challenge(challenge: Dict[str, Any]) -> None:
    """Render the 7-day eco challenge."""
    st.subheader(challenge.get("challenge_name") or "Your 7-Day Eco Challenge")

    daily_challenges = challenge.get("daily_challenges", [])
    if not daily_challenges:
        st.caption("No challenge was generated.")
        return

    for item in daily_challenges:
        st.markdown(
            f"""
            <div class="challenge-day">
                <div class="day-badge">Day {item.get("day", "")}</div>
                <div>
                    <strong>{item.get("task", "")}</strong>
                    <p class="muted">{item.get("impact", "")}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def report_has_content(report: Dict[str, Any]) -> bool:
    """Check whether the pipeline returned useful content."""
    return any(
        [
            bool(report.get("analysis")),
            bool(report.get("insights")),
            bool(report.get("recommendations")),
            bool(report.get("challenge")),
            bool(report.get("story")),
        ]
    )


def render_results(report: Dict[str, Any]) -> None:
    """Render the complete sustainability report."""
    analysis = report.get("analysis", {})
    insights = report.get("insights", {})
    recommendations = report.get("recommendations", {})
    challenge = report.get("challenge", {})
    story = report.get("story", "")

    st.header("Carbon Footprint Summary")
    render_metric_row(analysis, recommendations, challenge)

    left_col, right_col = st.columns([1.1, 0.9])

    with left_col:
        with st.container(border=True):
            st.subheader("Emission Breakdown")
            breakdown = analysis.get("category_breakdown", {})
            if isinstance(breakdown, dict):
                st.plotly_chart(build_breakdown_chart(breakdown), use_container_width=True)
            else:
                st.caption("Emission breakdown is not available.")

    with right_col:
        with st.container(border=True):
            st.subheader("Key Insights")
            render_list(insights.get("top_behaviors", []), "No top behaviors were generated.")
            st.markdown("**Root Causes**")
            render_list(insights.get("root_causes", []), "No root causes were generated.")
            st.markdown("**Opportunities**")
            render_list(insights.get("opportunities", []), "No opportunities were generated.")

    with st.container(border=True):
        st.subheader("Personalized Recommendations")
        render_recommendations(recommendations)

    challenge_col, story_col = st.columns([1, 1])

    with challenge_col:
        with st.container(border=True):
            st.subheader("7-Day Eco Challenge")
            render_challenge(challenge)

    with story_col:
        with st.container(border=True):
            st.subheader("Sustainability Story")
            if story:
                st.write(story)
            else:
                st.caption("No sustainability story was generated.")


def render_input_preview(user_data: Dict[str, Any]) -> None:
    """Render a compact preview of the submitted lifestyle data."""
    with st.container(border=True):
        st.subheader("Lifestyle Snapshot")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.caption("Transport")
        col1.write(user_data["transportation"]["primary_mode"])
        col2.caption("Electricity")
        col2.write(f'{user_data["electricity"]["monthly_kwh"]:.0f} kWh/mo')
        col3.caption("Food")
        col3.write(user_data["food"]["diet_type"])
        col4.caption("Waste")
        col4.write(f'{user_data["waste"]["trash_bags_per_week"]} bags/wk')
        col5.caption("Shopping")
        col5.write(f'{user_data["shopping"]["new_items_per_month"]} items/mo')


def main() -> None:
    """Run the Streamlit application."""
    apply_custom_css()
    render_hero()

    user_data, submitted = collect_user_data()
    render_input_preview(user_data)

    if submitted:
        try:
            pipeline = create_pipeline()
        except Exception as error:
            st.error(
                "The AI service could not be initialized. Add GROQ_API_KEY to your "
                ".env file, then refresh the app."
            )
            st.exception(error)
            return

        with st.spinner("Generating your AI-powered sustainability report..."):
            report = pipeline.generate_report(user_data)

        if not report_has_content(report):
            st.error(
                "The report could not be generated. Please check your Groq API key "
                "and internet connection, then try again."
            )
            return

        st.success("Your sustainability report is ready.")
        st.session_state["latest_report"] = report

    if "latest_report" in st.session_state:
        render_results(st.session_state["latest_report"])


if __name__ == "__main__":
    main()
