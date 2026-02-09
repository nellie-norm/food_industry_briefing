"""Core logic: Perplexity API calls, caching, briefing generation, and submissions."""

import json
import os
from datetime import datetime, timedelta

from openai import OpenAI

from config import (
    DATA_DIR,
    PERPLEXITY_BASE_URL,
    PERPLEXITY_MODEL,
    SECTIONS,
    SUBMISSIONS_DIR,
    SYSTEM_PROMPT,
)


def get_client(api_key: str) -> OpenAI:
    """Return an OpenAI client pointed at the Perplexity API."""
    return OpenAI(api_key=api_key, base_url=PERPLEXITY_BASE_URL)


def get_week_key(date=None, previous=False) -> str:
    """Return an ISO week key like '2026-W06' for the given date (default: today).
    If previous=True, returns the prior week."""
    if date is None:
        date = datetime.now()
    if previous:
        date = date - timedelta(days=7)
    return f"{date.isocalendar()[0]}-W{date.isocalendar()[1]:02d}"


def get_week_date_range(week_key: str) -> tuple[str, str]:
    """Return human-readable (start, end) date strings for an ISO week key."""
    year, week_num = int(week_key[:4]), int(week_key.split("W")[1])
    # Monday of that ISO week
    jan4 = datetime(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.weekday())
    monday = start_of_week1 + timedelta(weeks=week_num - 1)
    sunday = monday + timedelta(days=6)
    fmt = "%b %-d, %Y"
    return monday.strftime(fmt), sunday.strftime(fmt)


# --- Submissions ---


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)


def add_submission(week_key: str, url: str, note: str = "", submitted_by: str = ""):
    """Append a URL submission for a given week."""
    _ensure_dirs()
    path = os.path.join(SUBMISSIONS_DIR, f"{week_key}.json")
    submissions = load_submissions(week_key)
    submissions.append(
        {
            "url": url,
            "note": note,
            "submitted_by": submitted_by,
            "timestamp": datetime.now().isoformat(),
        }
    )
    with open(path, "w") as f:
        json.dump(submissions, f, indent=2)


def delete_submission(week_key: str, index: int):
    """Delete a submission by index for a given week."""
    _ensure_dirs()
    path = os.path.join(SUBMISSIONS_DIR, f"{week_key}.json")
    submissions = load_submissions(week_key)
    if 0 <= index < len(submissions):
        submissions.pop(index)
        with open(path, "w") as f:
            json.dump(submissions, f, indent=2)


def load_submissions(week_key: str) -> list[dict]:
    """Load all submissions for a given week."""
    _ensure_dirs()
    path = os.path.join(SUBMISSIONS_DIR, f"{week_key}.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def list_submission_weeks() -> list[str]:
    """List all weeks that have submissions."""
    _ensure_dirs()
    weeks = []
    for fname in os.listdir(SUBMISSIONS_DIR):
        if fname.endswith(".json"):
            weeks.append(fname.replace(".json", ""))
    return sorted(weeks, reverse=True)


# --- Briefing Cache ---


def save_briefing(week_key: str, briefing: dict):
    """Save a briefing dict to the cache."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, f"{week_key}.json")
    with open(path, "w") as f:
        json.dump(briefing, f, indent=2)


def load_briefing(week_key: str) -> dict | None:
    """Load a cached briefing, or None if not found."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, f"{week_key}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def list_cached_weeks() -> list[str]:
    """List all weeks with cached briefings."""
    _ensure_dirs()
    weeks = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json"):
            weeks.append(fname.replace(".json", ""))
    return sorted(weeks, reverse=True)


# --- Perplexity API ---


def fetch_section(
    client: OpenAI,
    section: dict,
    week_key: str,
    submitted_urls: list[dict],
) -> str:
    """Call Perplexity for a single briefing section. Returns markdown content."""
    start_date, end_date = get_week_date_range(week_key)

    user_prompt = (
        f"Find the most important {section['title'].lower()} developments in the "
        f"food industry for the week of {start_date} to {end_date}.\n\n"
        f"{section['prompt_focus']}"
    )

    if submitted_urls:
        urls_text = "\n".join(
            f"- {s['url']}" + (f" — {s['note']}" if s.get("note") else "")
            for s in submitted_urls
        )
        user_prompt += (
            f"\n\nAlso consider these stories submitted by our team:\n{urls_text}"
        )

    response = client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        extra_body={
            "search_domain_filter": section["domains"],
            "search_recency_filter": "week",
        },
    )

    return response.choices[0].message.content


def fetch_top3(client: OpenAI, briefing: dict) -> str:
    """Review all section content and identify the 3 most significant developments."""
    all_content = "\n\n".join(
        f"## {data['title']}\n{data['content']}"
        for data in briefing["sections"].values()
    )

    response = client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior food industry analyst. Review the following "
                    "weekly briefing sections and identify the 3 most significant "
                    "developments that food industry investors must know. For each, "
                    "write a single concise bullet point with a **bold lead-in** "
                    "explaining why it matters. Focus on decisive shifts, not "
                    "incremental news. Do NOT use numbered citations like [1]. "
                    "Include inline markdown hyperlinks where possible."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Here is the full briefing for {briefing['date_range']}:\n\n"
                    f"{all_content}\n\n"
                    "What are the 3 most significant developments this week for "
                    "food industry investors? Return exactly 3 markdown bullet points."
                ),
            },
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content


def generate_full_briefing(
    api_key: str,
    week_key: str,
    progress_callback=None,
) -> dict:
    """Generate a full briefing across all sections. Returns a briefing dict."""
    client = get_client(api_key)
    submissions = load_submissions(week_key)
    start_date, end_date = get_week_date_range(week_key)

    briefing = {
        "week_key": week_key,
        "date_range": f"{start_date} — {end_date}",
        "generated_at": datetime.now().isoformat(),
        "sections": {},
    }

    for i, section in enumerate(SECTIONS):
        if progress_callback:
            progress_callback(i, len(SECTIONS), section["title"])

        try:
            content = fetch_section(client, section, week_key, submissions)
        except Exception as e:
            content = f"*Error fetching this section: {e}*"

        briefing["sections"][section["id"]] = {
            "title": section["title"],
            "emoji": section["emoji"],
            "content": content,
        }

    # Generate Top 3 from all section content
    if progress_callback:
        progress_callback(len(SECTIONS), len(SECTIONS) + 1, "Top 3 highlights")

    try:
        briefing["top3"] = fetch_top3(client, briefing)
    except Exception as e:
        briefing["top3"] = f"*Error generating highlights: {e}*"

    if progress_callback:
        progress_callback(len(SECTIONS) + 1, len(SECTIONS) + 1, "Done")

    save_briefing(week_key, briefing)
    return briefing
