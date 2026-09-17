"""
explainer.py
------------
LangChain-powered natural-language explanation of the fuzzy inference
result. This is the SECOND use of the LLM in the pipeline (the first
being extraction in extractor.py).

IMPORTANT: The LLM here is strictly an explainer. It receives the
authoritative numerical score and category ALREADY computed by the
fuzzy inference engine (fuzzy/inference.py) and is explicitly instructed
never to alter them. This satisfies the project requirement that the
fuzzy engine — not the LLM — is authoritative for the numeric result.
"""

from dataclasses import dataclass
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ai.prompts import EXPLANATION_SYSTEM_PROMPT, EXPLANATION_HUMAN_TEMPLATE


@dataclass
class ExplanationResult:
    success: bool
    text: Optional[str]
    error_message: Optional[str] = None


FALLBACK_TEMPLATES = {
    "Very High": (
        "Your tank level is quite low relative to your household's water usage. "
        "Refilling as soon as possible is strongly recommended to avoid running out of water."
    ),
    "High": (
        "Your tank level is on the low side given your household's consumption. "
        "Refilling soon is recommended to stay ahead of demand."
    ),
    "Medium": (
        "Your tank level is moderate for your current usage pattern. "
        "It's a good idea to keep an eye on it and plan a refill in the near future."
    ),
    "Low": (
        "Your tank level is comfortably sufficient for your household's usage right now. "
        "No urgent action is needed, but continue to monitor it."
    ),
    "Very Low": (
        "Your tank is well-stocked relative to your household's needs. "
        "There is no immediate concern about running out of water."
    ),
}


def _build_explanation_chain(api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.4):
    llm = ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXPLANATION_SYSTEM_PROMPT),
            ("human", EXPLANATION_HUMAN_TEMPLATE),
        ]
    )
    return prompt | llm | StrOutputParser()


def generate_explanation(
    tank_capacity_liters: float,
    tank_level_percent: float,
    household_size: int,
    water_usage: str,
    urgency_score: float,
    urgency_category: str,
    api_key: str,
    model_name: str = "gpt-4o-mini",
) -> ExplanationResult:
    """
    Generates a natural-language explanation of an ALREADY-COMPUTED
    fuzzy inference result. Falls back to a canned template (still
    accurate, just less personalized) if the LLM call fails, so the
    application remains functional even without a working API key.
    """
    if not api_key:
        return ExplanationResult(
            success=True,
            text=FALLBACK_TEMPLATES.get(urgency_category, FALLBACK_TEMPLATES["Medium"]),
            error_message=(
                "AI explanation unavailable (no API key configured) — showing a "
                "standard template explanation instead."
            ),
        )

    try:
        chain = _build_explanation_chain(api_key=api_key, model_name=model_name)
        text = chain.invoke(
            {
                "tank_capacity_liters": tank_capacity_liters,
                "tank_level_percent": tank_level_percent,
                "household_size": household_size,
                "water_usage": water_usage,
                "urgency_score": urgency_score,
                "urgency_category": urgency_category,
            }
        )
        return ExplanationResult(success=True, text=text.strip())
    except Exception as exc:  # noqa: BLE001
        return ExplanationResult(
            success=True,
            text=FALLBACK_TEMPLATES.get(urgency_category, FALLBACK_TEMPLATES["Medium"]),
            error_message=f"AI explanation failed ({exc}); showing a standard template explanation instead.",
        )
