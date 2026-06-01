import logging
import subprocess
import json
import os
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def _find_gemini_cmd():
    """Find the gemini command, trying gemini.cmd on Windows as fallback."""
    import shutil
    try:
        if shutil.which("gemini"):
            return "gemini"
        if shutil.which("gemini.cmd"):
            return "gemini.cmd"
        # Last resort: check npm global bin
        npm_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm")
        gemini_cmd = os.path.join(npm_dir, "gemini.cmd")
        if os.path.exists(gemini_cmd):
            return gemini_cmd
        return None
    except Exception:
        return None


def check_gemini_installed() -> bool:
    """Verify 'gemini' command exists in PATH."""
    import shutil
    # Try multiple command names directly
    for cmd in ["gemini", "gemini.cmd", "gemini.CMD"]:
        try:
            r = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if r.returncode == 0:
                return True
        except Exception:
            continue
    # Fallback: try full path
    npm_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm")
    for cmd_name in ["gemini.cmd", "gemini.CMD"]:
        full = os.path.join(npm_dir, cmd_name)
        if os.path.isfile(full):
            try:
                r = subprocess.run(
                    [full, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                if r.returncode == 0:
                    return True
            except Exception:
                continue
    return False

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

def call_gemini(prompt: str, timeout: int = 60) -> str:
    """
    Execute Gemini CLI subprocess.
    Command: gemini generate --prompt "{prompt}"
    Returns raw stdout string.
    """
    # Ensure prompt is properly escaped for shell
    # We'll pass the prompt via stdin to avoid shell escaping issues
    gemini_cmd = _find_gemini_cmd()
    if not gemini_cmd:
        raise RuntimeError("Gemini CLI not found. Please install and ensure it's in PATH.")
    try:
        result = subprocess.run(
            [gemini_cmd, "generate"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True  # needed for shell scripts on Windows
        )
        if result.returncode != 0:
            raise RuntimeError(f"Gemini CLI failed: {result.stderr}")
        return result.stdout
    except subprocess.TimeoutExpired:
        raise RuntimeError("Gemini CLI timeout")

def extract_json_from_response(raw_response: str) -> Optional[Dict]:
    """
    Parse JSON from Gemini response.
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
    2. Call Gemini
    3. Extract JSON
    4. Return dict
    Raises exception if any step fails.
    """
    prompt = build_tailor_prompt(resume_text, job_description)
    raw_response = call_gemini(prompt)
    tailored_dict = extract_json_from_response(raw_response)
    if tailored_dict is None:
        # Fallback: retry once with stricter prompt
        strict_prompt = "Return ONLY valid JSON. No markdown, no explanations.\n\n" + prompt
        raw_response = call_gemini(strict_prompt)
        tailored_dict = extract_json_from_response(raw_response)
        if tailored_dict is None:
            raise ValueError("Failed to extract JSON from Gemini response after two attempts")
    return tailored_dict