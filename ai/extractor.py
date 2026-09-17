"""
extractor.py
------------
LangChain-powered natural-language -> structured-data extraction.

Pipeline:
    User's free-text description
        -> ChatPromptTemplate (system + human messages)
        -> ChatOpenAI (via LangChain)
        -> Pydantic-validated structured output (with_structured_output)
        -> ExtractionResult (validated, with missing-field detection)

Using LangChain's `with_structured_output` (backed by the LLM's native
function-calling / JSON schema mode) is preferred over manual string
parsing or regex because it is far more reliable: the LLM is constrained
to emit a schema-conformant object, and LangChain + Pydantic handle
parsing and validation errors for us.
"""

from dataclasses import dataclass
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ai.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_HUMAN_TEMPLATE
from utils.validation import (
    is_valid_capacity,
    is_valid_percent,
    is_valid_household_size,
    is_valid_usage_label,
)


class ExtractedWaterInfo(BaseModel):
    """Pydantic schema the LLM's structured output must conform to."""

    tank_capacity_liters: Optional[float] = Field(
        default=None, description="Total tank capacity in litres"
    )
    tank_level_percent: Optional[float] = Field(
        default=None, description="Current tank level as a percentage (0-100)"
    )
    household_size: Optional[int] = Field(
        default=None, description="Number of people in the household"
    )
    water_usage: str = Field(
        default="medium", description="Water usage level: low, medium, or high"
    )
    notes: Optional[str] = Field(default=None, description="Any other relevant detail")

    @field_validator("water_usage")
    @classmethod
    def normalize_usage(cls, v: str) -> str:
        v = (v or "medium").strip().lower()
        return v if v in ("low", "medium", "high") else "medium"


@dataclass
class ExtractionResult:
    success: bool
    data: Optional[ExtractedWaterInfo]
    missing_fields: List[str]
    error_message: Optional[str] = None


REQUIRED_FIELDS = ["tank_capacity_liters", "tank_level_percent", "household_size"]

FIELD_LABELS = {
    "tank_capacity_liters": "tank capacity (in litres)",
    "tank_level_percent": "current tank level (as a percentage)",
    "household_size": "number of people in the household",
}


def _build_extraction_chain(api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
    """
    Builds a LangChain chain: prompt -> LLM (structured output).
    temperature=0.0 is used deliberately for extraction, since we want
    deterministic, literal parsing rather than creative variation.
    """
    llm = ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)
    structured_llm = llm.with_structured_output(ExtractedWaterInfo)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXTRACTION_SYSTEM_PROMPT),
            ("human", EXTRACTION_HUMAN_TEMPLATE),
        ]
    )
    return prompt | structured_llm


def extract_water_info(
    user_input: str, api_key: str, model_name: str = "gpt-4o-mini"
) -> ExtractionResult:
    """
    Runs the LangChain extraction chain on a user's natural-language
    description and returns a validated ExtractionResult.

    Does NOT invent values: if the LLM legitimately could not find a
    required field in the text, that field is reported in
    `missing_fields` so the UI can prompt the user rather than silently
    guessing.
    """
    if not user_input or not user_input.strip():
        return ExtractionResult(
            success=False,
            data=None,
            missing_fields=[],
            error_message="Please describe your household water situation before analyzing.",
        )

    if not api_key:
        return ExtractionResult(
            success=False,
            data=None,
            missing_fields=[],
            error_message=(
                "No API key configured. Please set OPENAI_API_KEY in Streamlit "
                "secrets or your local .env file."
            ),
        )

    try:
        chain = _build_extraction_chain(api_key=api_key, model_name=model_name)
        parsed: ExtractedWaterInfo = chain.invoke({"user_input": user_input.strip()})
    except Exception as exc:  # noqa: BLE001 - surfaced to the user as a friendly message
        return ExtractionResult(
            success=False,
            data=None,
            missing_fields=[],
            error_message=f"AI extraction failed: {exc}",
        )

    # Determine which required fields are genuinely missing
    missing_fields = []
    if parsed.tank_capacity_liters is None or not is_valid_capacity(parsed.tank_capacity_liters):
        missing_fields.append("tank_capacity_liters")
    if parsed.tank_level_percent is None or not is_valid_percent(parsed.tank_level_percent):
        missing_fields.append("tank_level_percent")
    if parsed.household_size is None or not is_valid_household_size(parsed.household_size):
        missing_fields.append("household_size")
    if not is_valid_usage_label(parsed.water_usage):
        parsed.water_usage = "medium"  # safe fallback, always valid per schema

    return ExtractionResult(
        success=len(missing_fields) == 0,
        data=parsed,
        missing_fields=missing_fields,
    )


def missing_fields_message(missing_fields: List[str]) -> str:
    """Builds a user-friendly message listing which fields must be supplied manually."""
    if not missing_fields:
        return ""
    labels = [FIELD_LABELS.get(f, f) for f in missing_fields]
    if len(labels) == 1:
        joined = labels[0]
    else:
        joined = ", ".join(labels[:-1]) + " and " + labels[-1]
    return (
        f"I couldn't find your {joined} in that description. "
        "Please provide the missing value(s) below and I'll complete the analysis."
    )
