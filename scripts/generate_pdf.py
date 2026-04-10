#!/usr/bin/env python3
"""Generate a professional PDF from the MatadorAudit proposal markdown."""

import re
from fpdf import FPDF

CSUN_RED = (207, 10, 44)
DARK_GRAY = (51, 51, 51)
MED_GRAY = (102, 102, 102)
LIGHT_BG = (245, 245, 245)
WHITE = (255, 255, 255)

def sanitize(text: str) -> str:
    """Replace Unicode chars unsupported by latin-1 with ASCII equivalents."""
    replacements = {
        "\u2014": "--",  # em dash
        "\u2013": "-",   # en dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2022": "-",   # bullet
        "\u00a0": " ",   # nbsp
        "\u2192": "->",  # arrow
        "\u2265": ">=",  # >=
        "\u2264": "<=",  # <=
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Fallback: replace any remaining non-latin1 chars
    return text.encode("latin-1", errors="replace").decode("latin-1")


MD_PATH = "/home/cohedo/MatadorAudit/docs/proposal/matador-audit-proposal.md"
PDF_PATH = "/home/cohedo/MatadorAudit/docs/proposal/matador-audit-proposal.pdf"


class ProposalPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        self.is_title_page = False

    def header(self):
        if self.is_title_page or self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 8, "MatadorAudit: AI-Powered Fairness Auditing", align="L")
        self.cell(0, 8, "CSUN AI Jam 2026", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*CSUN_RED)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def footer(self):
        if self.is_title_page:
            return
        self.set_y(-20)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MED_GRAY)
        self.cell(0, 10, f"Page {self.page_no() - 1}", align="C")


def make_title_page(pdf: ProposalPDF):
    pdf.is_title_page = True
    pdf.add_page()

    # Red band at top
    pdf.set_fill_color(*CSUN_RED)
    pdf.rect(0, 0, pdf.w, 8, "F")

    # Title
    pdf.ln(45)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*CSUN_RED)
    pdf.multi_cell(0, 12, "MatadorAudit", align="C")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(0, 7, "AI-Powered Fairness Auditing\nfor University Systems", align="C")

    # Divider
    pdf.ln(10)
    cx = pdf.w / 2
    pdf.set_draw_color(*CSUN_RED)
    pdf.set_line_width(1)
    pdf.line(cx - 30, pdf.get_y(), cx + 30, pdf.get_y())
    pdf.ln(12)

    # Competition
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*CSUN_RED)
    pdf.cell(0, 8, "CSUN AI Jam 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*MED_GRAY)
    pdf.cell(0, 7, "AI & Ethics Track", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    # Team
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(0, 8, "Team Members", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Ido Cohen  (203866929)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Zach Bar  (202478542)", align="C", new_x="LMARGIN", new_y="NEXT")

    # Red band at bottom
    pdf.set_fill_color(*CSUN_RED)
    pdf.rect(0, pdf.h - 8, pdf.w, 8, "F")

    pdf.is_title_page = False


def render_table(pdf: ProposalPDF, rows: list[list[str]]):
    """Render a markdown table."""
    if not rows or len(rows) < 2:
        return
    headers = rows[0]
    data = rows[1:]  # skip separator row if present
    if data and all(re.match(r"^[-:|]+$", c.strip()) for c in data[0]):
        data = data[1:]

    n = len(headers)
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = usable / n

    # Header row
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(*CSUN_RED)
    pdf.set_text_color(*WHITE)
    for h in headers:
        pdf.cell(col_w, 7, h.strip(), border=1, fill=True, align="C")
    pdf.ln()

    # Data rows
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*DARK_GRAY)
    for i, row in enumerate(data):
        bg = (i % 2 == 0)
        if bg:
            pdf.set_fill_color(*LIGHT_BG)
        for j, cell in enumerate(row):
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", cell.strip())
            pdf.cell(col_w, 6, text, border=1, fill=bg, align="L")
        pdf.ln()
    pdf.ln(3)


def write_rich_line(pdf: ProposalPDF, text: str, font_size=10, indent=0):
    """Write a line with bold spans handled via multi_cell fragments."""
    pdf.set_x(pdf.l_margin + indent)
    # Split by bold markers
    parts = re.split(r"(\*\*.*?\*\*)", text)
    line_parts = []
    for p in parts:
        if p.startswith("**") and p.endswith("**"):
            line_parts.append(("B", p[2:-2]))
        else:
            line_parts.append(("", p))

    # Calculate if we need to use multi_cell (long text)
    total_text = text.replace("**", "")
    usable = pdf.w - pdf.l_margin - pdf.r_margin - indent

    # For simplicity with mixed bold, use write()
    for style, content in line_parts:
        pdf.set_font("Helvetica", style, font_size)
        pdf.write(5, content)
    pdf.ln(6)


def parse_and_render(pdf: ProposalPDF, md_text: str):
    lines = md_text.split("\n")
    i = 0
    in_code = False
    in_blockquote = False
    table_rows: list[list[str]] = []

    while i < len(lines):
        line = lines[i]

        # Code block toggle
        if line.strip().startswith("```"):
            if in_code:
                in_code = False
                pdf.ln(3)
            else:
                in_code = True
                pdf.set_font("Courier", "", 7)
                pdf.set_text_color(*MED_GRAY)
            i += 1
            continue

        if in_code:
            pdf.set_font("Courier", "", 7)
            pdf.set_text_color(*MED_GRAY)
            pdf.set_fill_color(*LIGHT_BG)
            pdf.cell(0, 4, line, fill=True, new_x="LMARGIN", new_y="NEXT")
            i += 1
            continue

        # Table detection
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(cells)
            i += 1
            continue
        elif table_rows:
            render_table(pdf, table_rows)
            table_rows = []

        stripped = line.strip()

        # Skip horizontal rules
        if re.match(r"^-{3,}$", stripped):
            i += 1
            continue

        # Empty line
        if not stripped:
            pdf.ln(3)
            i += 1
            continue

        # Headers
        if stripped.startswith("# ") and not stripped.startswith("## "):
            # Skip the main title (already on title page)
            i += 1
            continue

        if stripped.startswith("## "):
            text = stripped[3:]
            text = re.sub(r"\*\*.*?\*\*", "", text).strip()
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*CSUN_RED)
            pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*CSUN_RED)
            pdf.set_line_width(0.4)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(5)
            i += 1
            continue

        if stripped.startswith("### "):
            text = stripped[4:]
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(*CSUN_RED)
            pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            i += 1
            continue

        if stripped.startswith("#### "):
            text = stripped[5:]
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*DARK_GRAY)
            pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            i += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            if not in_blockquote:
                in_blockquote = True
                pdf.ln(2)
            text = stripped[2:]
            pdf.set_fill_color(235, 235, 240)
            pdf.set_x(pdf.l_margin + 5)
            pdf.set_draw_color(*CSUN_RED)
            # Draw left border
            y_before = pdf.get_y()
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*MED_GRAY)
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 5, clean, fill=True)
            y_after = pdf.get_y()
            pdf.set_line_width(1)
            pdf.line(pdf.l_margin + 3, y_before, pdf.l_margin + 3, y_after)
            i += 1
            continue
        elif in_blockquote:
            in_blockquote = False
            pdf.ln(3)

        # Bullet points
        if stripped.startswith("- "):
            text = stripped[2:]
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*DARK_GRAY)
            pdf.set_x(pdf.l_margin + 5)
            pdf.cell(5, 5, "-")
            pdf.set_x(pdf.l_margin + 12)
            # Handle bold in bullet
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 15, 5, clean)
            pdf.ln(1)
            i += 1
            continue

        # Numbered list
        m = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if m:
            num, text = m.group(1), m.group(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*CSUN_RED)
            pdf.set_x(pdf.l_margin + 5)
            pdf.cell(8, 5, f"{num}.")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*DARK_GRAY)
            clean = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 15, 5, clean)
            pdf.ln(1)
            i += 1
            continue

        # Regular paragraph
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*DARK_GRAY)
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
        pdf.multi_cell(0, 5, clean)
        pdf.ln(2)
        i += 1

    # Flush remaining table
    if table_rows:
        render_table(pdf, table_rows)


def main():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = sanitize(f.read())

    pdf = ProposalPDF()
    pdf.set_margin(20)

    make_title_page(pdf)
    pdf.add_page()
    parse_and_render(pdf, md_text)

    pdf.output(PDF_PATH)
    print(f"PDF generated: {PDF_PATH}")


if __name__ == "__main__":
    main()
