import json
import logging
import os
import re
from typing import Dict, Optional

import streamlit as st
from mistralai import Mistral

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "mistral-medium-3-5"


def check_mistral_installed() -> bool:
    """Verify Mistral API key is set in session state."""
    api_key = st.session_state.get("mistral_api_key", "")
    return bool(api_key and api_key.strip())


def build_tailor_prompt(resume_text: str, job_description: str) -> str:
    """Load prompt template and inject resume + JD."""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "tailor_resume.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as prompt_file:
            template = prompt_file.read()
    except FileNotFoundError:
        template = """You are an expert resume tailorer. Your task is to tailor the resume to match the job description while maintaining 100% factual honesty.

Rules:
1. Only restructure and rephrase existing content; never invent experience, skills, or qualifications.
2. Preserve all company names, job titles, dates, and degrees exactly.
3. Output must be valid JSON matching the Resume schema.
4. If you cannot tailor a section honestly, leave it as is.

Resume:
{resume_text}

Job Description:
{job_description}

Return ONLY the tailored resume in JSON format. Do not include any explanations, markdown, or additional text."""

    return template.replace("{resume_text}", resume_text).replace("{job_description}", job_description)


def call_mistral(prompt: str, timeout: int = 60) -> str:
    """Call the Mistral API and return the assistant response text."""
    api_key = st.session_state.get("mistral_api_key", "")
    if not api_key:
        raise RuntimeError("Mistral API key not configured. Please set it in the sidebar.")

    model = st.session_state.get("mistral_model", DEFAULT_MODEL)
    if not model or not model.strip():
        raise RuntimeError("Model name cannot be empty. Please enter a valid Mistral model name.")

    client = Mistral(api_key=api_key.strip())
    logger.info("Calling Mistral API with model: %s", model.strip())

    response = client.chat.complete(
        model=model.strip(),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=4000,
    )

    try:
        return response.choices[0].message.content or ""
    except (AttributeError, IndexError, KeyError) as exc:
        logger.error("Unexpected Mistral response format: %s", exc)
        raise RuntimeError(f"Unexpected Mistral response format: {exc}") from exc


def extract_json_from_response(raw_response: str) -> Optional[Dict]:
    """Parse JSON from Mistral response text."""
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_response)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = raw_response.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        start = json_str.find("{")
        end = json_str.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(json_str[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def tailor_resume(resume_text: str, job_description: str) -> Dict:
    """Build prompt, call Mistral, and return parsed JSON."""
    prompt = build_tailor_prompt(resume_text, job_description)
    raw_response = call_mistral(prompt)
    tailored_dict = extract_json_from_response(raw_response)
    if tailored_dict is None:
        strict_prompt = "Return ONLY valid JSON. No markdown, no explanations.\n\n" + prompt
        raw_response = call_mistral(strict_prompt)
        tailored_dict = extract_json_from_response(raw_response)
        if tailored_dict is None:
            raise ValueError("Failed to extract JSON from Mistral response after two attempts")
    return tailored_dict
