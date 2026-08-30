import os
import json

from dotenv import load_dotenv
from google import genai

from extract_resume import extract_resume_text


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found. Check your .env file.")
    exit()


client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"


def build_prompt(resume_text, job_description):
    prompt = f"""
You are an expert technical recruiter and resume reviewer.

Compare the RESUME below to the JOB DESCRIPTION below, and evaluate
how well the candidate matches the role.

Respond ONLY with valid JSON (no markdown, no code fences, no extra text)
in exactly this structure:

{{
    "match_score": <integer 0-100>,
    "summary": "<one or two sentence overall verdict>",
    "strengths": [
        "<point 1>",
        "<point 2>",
        "..."
    ],
    "gaps": [
        "<point 1>",
        "<point 2>",
        "..."
    ],
    "suggestions": [
        "<specific actionable improvement 1>",
        "<specific actionable improvement 2>",
        "..."
    ]
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    return prompt.strip()


def analyze_resume(resume_text, job_description):
    prompt = build_prompt(resume_text, job_description)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    raw_text = response.text.strip()

    # Remove markdown code fences if Gemini returns them
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")

        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        result = json.loads(raw_text)

    except json.JSONDecodeError:
        print(
            "WARNING: Could not parse Gemini's response as JSON. "
            "Raw response was:"
        )
        print(raw_text)
        return None

    return result


def print_analysis(result):
    if result is None:
        return

    print("\n" + "=" * 50)
    print(f"MATCH SCORE: {result.get('match_score')}/100")
    print("=" * 50)

    print(f"\nSummary: {result.get('summary')}\n")

    print("Strengths:")
    for item in result.get("strengths", []):
        print(f" + {item}")

    print("\nGaps:")
    for item in result.get("gaps", []):
        print(f" - {item}")

    print("\nSuggestions:")
    for item in result.get("suggestions", []):
        print(f" * {item}")

    print()


if __name__ == "__main__":
    resume_path = input(
        "Enter the path to a resume file (.pdf or .docx): "
    ).strip('"')

    if not os.path.exists(resume_path):
        print(f"ERROR: File not found at: {resume_path}")
        exit()

    print(
        "\nPaste the job description below, then press Enter "
        "and type END on its own line:"
    )

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    job_description_text = "\n".join(lines)

    resume_text = extract_resume_text(resume_path)

    print("\nAnalyzing... (this may take a few seconds)")

    result = analyze_resume(
        resume_text,
        job_description_text
    )

    print_analysis(result)