"""Streamlit app — Food Industry Weekly Briefing Tool."""

import os

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from briefing_engine import (
    add_submission,
    delete_submission,
    generate_full_briefing,
    get_week_date_range,
    get_week_key,
    list_cached_weeks,
    load_briefing,
    load_submissions,
)
import re

from config import SECTIONS
from export import briefing_to_markdown, briefing_to_pdf


def _normalize_content(text: str) -> str:
    """Normalize markdown content for consistent display.

    - Convert ### headings to bold sub-headers
    - Escape $ to prevent LaTeX rendering
    """
    # Convert ### / ## / # headings within content to bold sub-headers
    text = re.sub(r"^#{1,3}\s+(.+)$", r"**\1**", text, flags=re.MULTILINE)
    # Escape dollar signs
    text = text.replace("$", "\\$")
    return text

# --- Page config ---

st.set_page_config(
    page_title="Food Industry Briefing",
    page_icon="\U0001F4CB",
    layout="wide",
)

# Constrain width for readability
st.markdown(
    """
    <style>
    .block-container { max-width: 900px; margin: auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---

with st.sidebar:
    st.title("\U0001F4CB Food Briefing")
    st.markdown("---")

    # API key
    api_key = st.text_input(
        "Perplexity API Key",
        type="password",
        value=os.environ.get("PERPLEXITY_API_KEY", ""),
        help="Get your key at https://www.perplexity.ai/settings/api",
    )

    st.markdown("---")

    # Week selector — default to previous week
    previous_week = get_week_key(previous=True)
    current_week = get_week_key()
    cached_weeks = list_cached_weeks()
    all_weeks = sorted(set([previous_week, current_week] + cached_weeks), reverse=True)

    default_index = all_weeks.index(previous_week) if previous_week in all_weeks else 0
    selected_week = st.selectbox(
        "Select week",
        all_weeks,
        index=default_index,
        format_func=lambda w: f"{w}  ({get_week_date_range(w)[0]} – {get_week_date_range(w)[1]})",
    )

    # Regenerate option
    cache_exists = selected_week in cached_weeks
    regenerate = False
    if cache_exists:
        regenerate = st.checkbox("Regenerate (replace saved version)", value=False)

    st.markdown("---")

    # Generate button
    generate_clicked = st.button(
        "\U0001F680 Generate Briefing",
        type="primary",
        use_container_width=True,
        disabled=not api_key,
    )

    if not api_key:
        st.caption("Enter your API key above to generate briefings.")

# --- Main area ---

tab_briefing, tab_submit = st.tabs(["\U0001F4C4 Briefing", "\U0001F4E5 Submit Stories"])

# --- Tab 1: Briefing ---

with tab_briefing:
    briefing = None

    # Handle generation
    if generate_clicked and api_key:
        if cache_exists and not regenerate:
            briefing = load_briefing(selected_week)
            st.info("Loaded a previously saved briefing. Check 'Regenerate' in the sidebar to create a fresh one.")
        else:
            progress_bar = st.progress(0, text="Starting briefing generation...")

            def update_progress(current, total, section_name):
                pct = current / total
                if current < total:
                    progress_bar.progress(pct, text=f"Researching: {section_name}...")
                else:
                    progress_bar.progress(1.0, text="Briefing complete!")

            with st.spinner("Generating briefing..."):
                briefing = generate_full_briefing(
                    api_key, selected_week, progress_callback=update_progress
                )
            st.success("Briefing generated and cached!")
    else:
        # Try to load from cache
        briefing = load_briefing(selected_week)

    # Display briefing
    if briefing:
        start_date, end_date = get_week_date_range(selected_week)
        st.markdown(f"## {start_date} — {end_date}")

        # Export buttons
        col1, col2, col3 = st.columns([6, 1, 1])
        with col2:
            md_content = briefing_to_markdown(briefing)
            st.download_button(
                "\U0001F4DD MD",
                data=md_content,
                file_name=f"briefing-{selected_week}.md",
                mime="text/markdown",
            )
        with col3:
            pdf_bytes = briefing_to_pdf(briefing)
            st.download_button(
                "\U0001F4C4 PDF",
                data=pdf_bytes,
                file_name=f"briefing-{selected_week}.pdf",
                mime="application/pdf",
            )

        # Top 3 highlights
        if briefing.get("top3"):
            st.markdown("#### Key Developments This Week")
            st.markdown(_normalize_content(briefing["top3"]))

        st.markdown("---")

        # Sections
        for section in SECTIONS:
            data = briefing["sections"].get(section["id"])
            if not data:
                continue
            with st.expander(f"{data['emoji']} {data['title']}", expanded=True):
                st.markdown(_normalize_content(data["content"]))

        # Footer
        st.markdown("---")
        generated_at = briefing.get("generated_at", "")[:16].replace("T", " ")
        st.caption(f"Generated: {generated_at}")
    else:
        st.markdown("## Welcome")
        st.markdown(
            "No briefing for this week yet. Enter your Perplexity API key in the "
            "sidebar and click **Generate Briefing** to create one.\n\n"
            "Past briefings are saved automatically — use the **week selector** "
            "in the sidebar to browse previous weeks.\n\n"
            "You can also switch to the **Submit Stories** tab to add URLs for "
            "the team to review."
        )

# --- Tab 2: Submit Stories ---

with tab_submit:
    st.subheader(f"\U0001F4E5 Submit Stories for {selected_week}")
    st.markdown(
        "Add URLs throughout the week. They'll be included when the briefing is generated."
    )

    with st.form("submit_url", clear_on_submit=True):
        url = st.text_input("URL *", placeholder="https://...")
        note = st.text_input("Note (optional)", placeholder="Brief description")
        submitted_by = st.text_input("Your name (optional)")
        submitted = st.form_submit_button("Submit", type="primary")

        if submitted:
            if url and url.startswith("http"):
                add_submission(selected_week, url, note, submitted_by)
                st.success("Story submitted!")
                st.rerun()
            else:
                st.error("Please enter a valid URL starting with http.")

    st.markdown("---")
    st.markdown("#### Submitted stories")

    submissions = load_submissions(selected_week)
    if not submissions:
        st.caption("No stories submitted for this week yet.")
    else:
        # Show newest first
        for i, sub in enumerate(reversed(submissions)):
            real_index = len(submissions) - 1 - i
            col_content, col_delete = st.columns([9, 1])
            with col_content:
                link = f"[{sub['url']}]({sub['url']})"
                parts = [f"**{link}**"]
                if sub.get("note"):
                    parts.append(f"  \n{sub['note']}")
                meta = []
                if sub.get("submitted_by"):
                    meta.append(sub["submitted_by"])
                if sub.get("timestamp"):
                    meta.append(sub["timestamp"][:16].replace("T", " "))
                if meta:
                    parts.append(f"  \n*{' · '.join(meta)}*")
                st.markdown("\n".join(parts))
            with col_delete:
                if st.button("\U0001F5D1", key=f"del_{real_index}"):
                    delete_submission(selected_week, real_index)
                    st.rerun()
            st.markdown("---")
