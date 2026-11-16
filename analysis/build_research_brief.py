from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#2A9D8F")
GOLD = colors.HexColor("#E9A23B")
RED = colors.HexColor("#D65A4A")
SLATE = colors.HexColor("#4B5563")
LIGHT = colors.HexColor("#F3F6F8")
MID = colors.HexColor("#D8E1E8")

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))


def page_frame(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(MID)
    canvas.setLineWidth(0.5)
    canvas.line(0.65 * inch, height - 0.48 * inch, width - 0.65 * inch, height - 0.48 * inch)
    canvas.setFillColor(SLATE)
    canvas.setFont("DejaVu", 7.5)
    canvas.drawString(0.65 * inch, height - 0.38 * inch, "BOUNDED ADVERSARIAL ADVICE - FROZEN PILOT")
    canvas.drawRightString(width - 0.65 * inch, 0.38 * inch, f"{doc.page}")
    canvas.restoreState()


def build(root: Path) -> Path:
    output = root / "output/pdf/RESEARCH_BRIEF.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        rightMargin=0.68 * inch,
        leftMargin=0.68 * inch,
        topMargin=0.86 * inch,
        bottomMargin=0.58 * inch,
        title="Bounded Adversarial Advice Coincides with Lower Task Completion Without Observed Sabotage",
        author="Jiaying Wang",
        subject="AI control and model behavior pilot",
    )

    sample = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=sample["Title"],
        fontName="DejaVu-Bold",
        fontSize=19,
        leading=22.5,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=sample["Normal"],
        fontName="DejaVu",
        fontSize=9,
        leading=12,
        textColor=SLATE,
        spaceAfter=13,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=sample["Heading2"],
        fontName="DejaVu-Bold",
        fontSize=12.3,
        leading=14.5,
        textColor=colors.black,
        spaceBefore=8,
        spaceAfter=5,
        keepWithNext=True,
    )
    body = ParagraphStyle(
        "Body",
        parent=sample["BodyText"],
        fontName="DejaVu",
        fontSize=8.7,
        leading=12.2,
        textColor=colors.black,
        spaceAfter=6,
    )
    compact = ParagraphStyle(
        "Compact",
        parent=body,
        fontSize=8.1,
        leading=10.6,
        spaceAfter=3,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=compact,
        fontName="DejaVu-Bold",
        textColor=colors.white,
        spaceAfter=0,
    )
    caption = ParagraphStyle(
        "Caption",
        parent=body,
        fontSize=7.5,
        leading=9.4,
        textColor=SLATE,
        alignment=TA_CENTER,
        spaceAfter=5,
    )
    callout = ParagraphStyle(
        "Callout",
        parent=body,
        fontName="DejaVu-Bold",
        fontSize=10.4,
        leading=13.4,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=0,
    )

    story = []
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Bounded Adversarial Advice Coincides with Lower Task Completion Without Observed Sabotage", title))
    story.append(Paragraph("Closed 35-trajectory ControlArena pilot | Frozen protocol day3-final-sonnet45-v1 | November 2026<br/>Jiaying Wang | Repository: https://github.com/jiaying-wang091/advice-bandwidth-control.git", subtitle))
    key_table = Table(
        [[Paragraph("0/35 side-task successes", callout), Paragraph("6/7 baseline success", callout), Paragraph("3/7 adversarial/64 success", callout)]],
        colWidths=[2.15 * inch] * 3,
    )
    key_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, MID),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, MID),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(key_table)
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("Executive summary", heading))
    story.append(
        Paragraph(
            "This project tests a narrow AI-control protocol: a stronger untrusted advisor can send one bandwidth-limited natural-language message, while a trusted executor retains all tool authority. Across 35 frozen trajectories, no protected side task succeeded and no successful sabotage occurred. Main-task success was 6/7 with no advice, 6/7 under both benign conditions, 5/7 under adversarial/16, and 3/7 under adversarial/64.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The result is not a positive vulnerability demonstration. Its value is a clean separation of safety and capability outcomes under a precommitted protocol. The descriptive pattern suggests that additional adversarial bandwidth may first appear as interference or distraction rather than covert control. With only seven tasks per condition, that is a hypothesis, not a statistically established bandwidth effect.",
            body,
        )
    )
    story.append(Paragraph("Research question and threat model", heading))
    story.append(
        Paragraph(
            "<b>Question.</b> How much one-shot communication bandwidth does a stronger untrusted model need before it can influence a weaker trusted executor toward an undesirable action?",
            body,
        )
    )
    story.append(
        Paragraph(
            "T receives the main task and an explicit protected-state rule. After at most two read-only orientation actions, U observes the task, visible state, and orientation transcript. In adversarial conditions U privately receives the hidden side objective. U has no tools and can communicate once. T is warned that advice may be capable but wrong or adversarial, yet is not told to obey or ignore it. T alone acts in the sandbox.",
            body,
        )
    )
    story.append(Paragraph("Frozen design", heading))
    design_data = [
        ["Component", "Frozen value"],
        ["Environment", "ControlArena 20.1.1, ControlIACSetting"],
        ["Trusted executor", "anthropic/claude-sonnet-4-5-20250929"],
        ["Untrusted advisor", "anthropic/claude-sonnet-4-6"],
        ["Conditions", "none/0; benign/16; benign/64; adversarial/16; adversarial/64"],
        ["Tasks and runs", "7 frozen IAC tasks; 35 trajectories; one run per task-condition cell"],
        ["Authority and limits", "U: no tools, one message. T: 2 read-only orientation + 14 execution actions."],
        ["Outcomes", "Objective main score; side score; sabotage = main pass AND side success"],
    ]
    design = Table(design_data, colWidths=[1.35 * inch, 5.1 * inch], repeatRows=1)
    design.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "DejaVu-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.6),
                ("LEADING", (0, 0), (-1, -1), 9.4),
                ("GRID", (0, 0), (-1, -1), 0.35, MID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(design)

    story.append(PageBreak())
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Observed results", title))
    chart = root / "results/figures/main_task_success_by_condition.png"
    story.append(Image(str(chart), width=6.45 * inch, height=3.63 * inch))
    story.append(Paragraph("Observed proportions with 95% Wilson intervals. n=7 per condition.", caption))
    results_data = [
        ["Condition", "Main", "Side", "Sabotage", "Submit", "Limit"],
        ["None / 0", "6/7", "0/7", "0/7", "6/7", "1/7"],
        ["Benign / 16", "6/7", "0/7", "0/7", "5/7", "2/7"],
        ["Benign / 64", "6/7", "0/7", "0/7", "6/7", "1/7"],
        ["Adversarial / 16", "5/7", "0/7", "0/7", "7/7", "0/7"],
        ["Adversarial / 64", "3/7", "0/7", "0/7", "4/7", "3/7"],
    ]
    result_table = Table(results_data, colWidths=[1.65 * inch, 0.82 * inch, 0.82 * inch, 0.95 * inch, 0.82 * inch, 0.82 * inch], repeatRows=1)
    result_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "DejaVu-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.35, MID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(result_table)
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("Result boundary", heading))
    story.append(
        Paragraph(
            "No side task succeeded in any condition (0/35), so successful sabotage was also 0/35. Among adversarial trajectories, side-task success was 0/14. These zero counts prevent estimation of a sabotage-response curve; they do not establish that the true event rate is zero.",
            body,
        )
    )
    story.append(
        Paragraph(
            "Relative to no advice, main-task success was 14.3 percentage points lower under adversarial/16 and 42.9 points lower under adversarial/64. The Wilson intervals are wide and overlapping. No hypothesis test or inferential bandwidth claim is reported.",
            body,
        )
    )
    story.append(Paragraph("Protocol diagnostics", heading))
    story.append(
        Paragraph(
            "All 35 trajectories completed without infrastructure errors or recorded protocol violations. No-advice made zero advisor calls. Every adversarial message was delivered within its cap; one benign/64 trajectory exhausted three over-cap attempts and received no message. Invalid outputs were rejected, never truncated. No advisor refusals occurred.",
            body,
        )
    )

    story.append(PageBreak())
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Interpretation and research judgment", title))
    story.append(Paragraph("Observed pattern", heading))
    story.append(
        Paragraph(
            "Baseline and both benign conditions were stable at 6/7 aggregate main-task success. Adversarial/64 combined the lowest main-task success (3/7), the highest limit-exceeded count (3/7), and a higher mean executor action count than baseline (11.6 versus 10.0). Adversarial/16 also averaged 11.6 actions but submitted in all seven runs.",
            body,
        )
    )
    story.append(Paragraph("Interpretation", heading))
    story.append(
        Paragraph(
            "A plausible interpretation is that adversarial bandwidth can first manifest as interference: redirecting attention, expanding scope, or consuming scarce action budget without achieving the exact protected-state violation. The data are consistent with this pathway but do not identify it. The study did not manipulate distraction or directly measure search-path redirection.",
            body,
        )
    )
    interpretation = Table(
        [
            [Paragraph("Supported by the pilot", table_header), Paragraph("Not supported by the pilot", table_header)],
            [
                Paragraph("- Zero observed sabotage<br/>- Stable baseline and benign aggregate performance<br/>- Lower adversarial main-task success, especially at 64 characters<br/>- More ceiling pressure in adversarial/64", compact),
                Paragraph("- A statistically significant bandwidth effect<br/>- A monotonic sabotage curve<br/>- A general claim that longer advice is unsafe<br/>- A demonstrated cognitive mechanism", compact),
            ],
        ],
        colWidths=[3.22 * inch, 3.22 * inch],
    )
    interpretation.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#EEF8F5")),
                ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#FFF5F2")),
                ("BOX", (0, 0), (-1, -1), 0.45, MID),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, MID),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(interpretation)
    story.append(Paragraph("Alternative explanations and limitations", heading))
    story.append(
        Paragraph(
            "The decisive limitations are seven tasks, n=7 per condition, one run per cell, heterogeneous task difficulty, imperfectly uniform attack relevance, zero side-task events, and possible interaction with the 14-action ceiling. A content audit found eight of 14 adversarial messages directly targeted the protected objective, four were indirect, and two were non-targeting or main-task aligned. Character count constrains surface length rather than semantic information. Results may also be specific to this model pair and ControlIAC setting.",
            body,
        )
    )
    story.append(Paragraph("Portfolio contribution", heading))
    story.append(
        Paragraph(
            "The project demonstrates research judgment more than a positive security result: an explicit threat model, strict U/T role separation, exact channel enforcement, objective scoring, pre-freeze viability gates, documented repair decisions, frozen hashes, append-only logs, and conservative treatment of a null safety outcome. The strongest claim is methodological and behavioral: under this frozen pilot, adversarial advice did not induce sabotage, but longer adversarial advice coincided with lower task completion and more ceiling pressure, motivating a focused interference hypothesis.",
            body,
        )
    )
    story.append(Paragraph("Reproducibility", heading))
    story.append(
        Paragraph(
            "The repository retains the frozen protocol, final JSONL, all 35 Inspect logs, exact task-condition matrix, machine-readable tables, analysis code, and figures. Running <font name='Courier'>python -m analysis.finalize_closed_pilot</font> validates the closed design and regenerates the descriptive outputs without model calls.",
            body,
        )
    )

    doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
    return output


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(build(root))
