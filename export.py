"""Markdown and PDF export for briefings."""

import re

from fpdf import FPDF

from config import SECTIONS


def briefing_to_markdown(briefing: dict) -> str:
    """Convert a briefing dict to a clean markdown document."""
    lines = [
        f"# Food Industry Weekly Briefing",
        f"### {briefing['date_range']}",
        "",
    ]

    if briefing.get("top3"):
        lines.append("## Key Developments This Week")
        lines.append("")
        lines.append(briefing["top3"])
        lines.append("")
        lines.append("---")
        lines.append("")

    for section in SECTIONS:
        data = briefing["sections"].get(section["id"])
        if not data:
            continue
        lines.append(f"## {data['emoji']} {data['title']}")
        lines.append("")
        lines.append(data["content"])
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated: {briefing['generated_at'][:16].replace('T', ' ')}*")
    return "\n".join(lines)


class _BriefingPDF(FPDF):
    """Custom PDF with header/footer for the briefing."""

    def __init__(self, date_range: str):
        super().__init__()
        self.date_range = date_range

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Food Industry Weekly Briefing", align="L")
        self.cell(0, 8, self.date_range, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _sanitize_for_latin1(text: str) -> str:
    """Replace characters that Helvetica/latin-1 can't render."""
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u2022": "-",    # bullet
        "\u00a0": " ",    # non-breaking space
        "\u2010": "-",    # hyphen
        "\u2011": "-",    # non-breaking hyphen
        "\u2012": "-",    # figure dash
        "\u2032": "'",    # prime
        "\u2033": '"',    # double prime
        "\u20ac": "EUR",  # euro sign (not in latin-1 core fonts)
        "\u2122": "(TM)", # trademark
        "\u2020": "+",    # dagger
        "\u2021": "++",   # double dagger
        "\u2039": "<",    # single left angle quote
        "\u203a": ">",    # single right angle quote
        "\u00ab": "<<",   # left double angle quote
        "\u00bb": ">>",   # right double angle quote
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    # Drop any remaining non-latin-1 characters silently (no ? marks)
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def _strip_markdown_links(text: str) -> str:
    """Convert [text](url) to 'text (url)' for plain-text rendering."""
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)


def _render_markdown_line(pdf: FPDF, line: str):
    """Render a single line of markdown-ish text into the PDF, handling bold and italic."""
    line = _strip_markdown_links(line)
    line = _sanitize_for_latin1(line)
    # Split on bold (**text**) and italic (*text*) markers
    parts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", line)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.write(5, part[2:-2])
        elif part.startswith("*") and part.endswith("*"):
            pdf.set_font("Helvetica", "I", 10)
            pdf.write(5, part[1:-1])
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.write(5, part)
    pdf.ln(6)


def briefing_to_pdf(briefing: dict) -> bytes:
    """Convert a briefing dict to PDF bytes."""
    pdf = _BriefingPDF(_sanitize_for_latin1(briefing["date_range"]))
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 12, "Food Industry Weekly Briefing", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, _sanitize_for_latin1(briefing["date_range"]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Top 3 highlights
    if briefing.get("top3"):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 10, "Key Developments This Week", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(37, 99, 235)
        pdf.line(10, pdf.get_y(), 80, pdf.get_y())
        pdf.ln(3)
        pdf.set_text_color(30, 30, 30)
        for line in briefing["top3"].split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(2)
                continue
            if line.startswith("- ") or line.startswith("* "):
                pdf.set_font("Helvetica", "", 10)
                pdf.write(5, "  -  ")
                _render_markdown_line(pdf, line[2:])
            else:
                _render_markdown_line(pdf, line)
        pdf.ln(6)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

    for section in SECTIONS:
        data = briefing["sections"].get(section["id"])
        if not data:
            continue

        # Section heading
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(37, 99, 235)
        # Use ASCII fallback for emoji in PDF (fpdf2 Helvetica doesn't support emoji)
        pdf.cell(
            0, 10, f"{data['title']}", new_x="LMARGIN", new_y="NEXT"
        )
        pdf.set_draw_color(37, 99, 235)
        pdf.line(10, pdf.get_y(), 80, pdf.get_y())
        pdf.ln(3)

        # Section content
        pdf.set_text_color(30, 30, 30)
        content = data["content"]
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(2)
                continue
            # Handle markdown subheadings (###, ##, #)
            if line.startswith("#"):
                heading_text = line.lstrip("#").strip()
                heading_text = _sanitize_for_latin1(heading_text)
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(30, 30, 30)
                pdf.cell(0, 7, heading_text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
                pdf.set_text_color(30, 30, 30)
            # Handle bullet points
            elif line.startswith("- ") or line.startswith("* "):
                pdf.set_font("Helvetica", "", 10)
                pdf.write(5, "  -  ")
                _render_markdown_line(pdf, line[2:])
            else:
                _render_markdown_line(pdf, line)

        pdf.ln(4)

    # Footer timestamp
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(
        0, 5,
        f"Generated: {briefing['generated_at'][:16].replace('T', ' ')}",
        new_x="LMARGIN", new_y="NEXT",
    )

    return bytes(pdf.output())
