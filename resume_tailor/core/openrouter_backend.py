import logging
import os
import json
import re
from typing import Optional, Dict
import requests
import streamlit as st

logger = logging.getLogger(__name__)

# Default model
DEFAULT_MODEL = "openrouter/gpt-3.5-turbo"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

def check_openrouter_installed() -> bool:
    """Verify OpenRouter API key is set in session state."""
    api_key = st.session_state.get("openrouter_api_key", "")
    return bool(api_key and api_key.strip())

def build_tailor_prompt(resume_text: str, job_description: str) -> str:
    """Load prompt template and inject resume + JD."""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "tailor_resume.txt")
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        # Fallback template if file not found
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

def call_openrouter(prompt: str, timeout: int = 60) -> str:
    """
    Call OpenRouter API via HTTP.
    Returns raw response string.
    """
    api_key = st.session_state.get("openrouter_api_key", "")
    if not api_key:
        raise RuntimeError("OpenRouter API key not configured. Please set it in the sidebar.")

    model = st.session_state.get("openrouter_model", DEFAULT_MODEL)

    # Validate model is not empty
    if not model or not model.strip():
        raise RuntimeError("Model name cannot be empty. Please enter a valid OpenRouter model name.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model.strip(),
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Consider adding parameters for deterministic output if needed
        "temperature": 0.1,
        "max_tokens": 4000
    }

    # Log the request for debugging (without exposing API key)
    logger.info(f"Calling OpenRouter API with model: {model.strip()}")
    logger.debug(f"Request payload: {json.dumps({k: v for k, v in payload.items() if k != 'messages'}|{'messages': '[PROMPT TRUNCATED]'})}")

    try:
        response = requests.post(
            f"{OPENROUTER_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )

        # If we get an HTTP error, try to get more details from the response
        if not response.ok:
            try:
                error_detail = response.json()
                error_message = error_detail.get('error', {}).get('message', response.text)
                logger.error(f"OpenRouter API error: {error_detail}")
                raise RuntimeError(f"OpenRouter API error: {error_message}")
            except json.JSONDecodeError:
                logger.error(f"OpenRouter API error: {response.text}")
                raise RuntimeError(f"OpenRouter API error: {response.text}")

        response.raise_for_status()
        result = response.json()
        # Extract the assistant's message content
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            content = message.get("content", "")
            logger.info(f"Successfully received response from OpenRouter API")
            return content
        else:
            logger.error(f"Unexpected OpenRouter response format: {result}")
            raise RuntimeError(f"Unexpected OpenRouter response format: {result}")
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        # Try to get more details from the exception
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_message = error_detail.get('error', {}).get('message', str(e))
                raise RuntimeError(f"OpenRouter API failed: {error_message}")
            except:
                raise RuntimeError(f"OpenRouter API failed: {str(e)}")
        else:
            raise RuntimeError(f"OpenRouter API failed: {str(e)}")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse OpenRouter response: {e}")
        raise RuntimeError(f"Failed to parse OpenRouter response: {str(e)}")

def extract_json_from_response(raw_response: str) -> Optional[Dict]:
    """
    Parse JSON from OpenRouter response.
    Handles markdown code blocks (```json ... ```).
    Returns dict or None if parsing fails.
    """
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response)
    if json_match:
        json_str = json_match.group(1)
    else:
        # If no code block, assume the entire response is JSON
        json_str = raw_response.strip()

    # Try to parse JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON object with regex (simple attempt)
        # Look for content between first { and last }
        start = json_str.find('{')
        end = json_str.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = json_str[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return None

def tailor_resume(resume_text: str, job_description: str) -> Dict:
    """
    Full pipeline:
    1. Build prompt
    2. Call OpenRouter
    3. Extract JSON
    4. Return dict
    Raises exception if any step fails.
    """
    prompt = build_tailor_prompt(resume_text, job_description)
    raw_response = call_openrouter(prompt)
    tailored_dict = extract_json_from_response(raw_response)
    if tailored_dict is None:
        # Fallback: retry once with stricter prompt
        strict_prompt = "Return ONLY valid JSON. No markdown, no explanations.\n\n" + prompt
        raw_response = call_openrouter(strict_prompt)
        tailored_dict = extract_json_from_response(raw_response)
        if tailored_dict is None:
            raise ValueError("Failed to extract JSON from OpenRouter response after two attempts")
    return tailored_dict