import os
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from config import APP_NAME

PRIMARY = colors.HexColor("#203a43")
LIGHT = colors.HexColor("#eef2f5")


def grade_from_percentage(pct):
    """Badilisha mizani hii kulingana na chuo chako."""
    if pct >= 70:
        return "A"
    if pct >= 60:
        return "B"
    if pct >= 50:
        return "C"
    if pct >= 40:
        return "D"
    return "F"


def _p(text, style):
    return Paragraph(escape(str(text if text is not None else "-")), style)


def _table_style(header_rows=1):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, header_rows - 1), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), colors.white),
        ("FONTNAME", (0, 0), (-1, header_rows - 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, header_rows), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5ccd3")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def build_student_report(student, marks_df, att_summary_df):
    """Rudisha bytes za PDF ya report ya mwanafunzi."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title=f"Student Report - {student.get('full_name', '')}",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Title"], textColor=PRIMARY, fontSize=18, spaceAfter=2)
    sub = ParagraphStyle("s", parent=styles["Normal"], alignment=1, textColor=colors.grey, fontSize=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=PRIMARY, spaceBefore=14, spaceAfter=6)
    cell = ParagraphStyle("c", parent=styles["Normal"], fontSize=9)

    story = []

    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=3.2 * cm, height=3.2 * cm, kind="proportional")
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 4))
        except Exception:
            pass

    story.append(Paragraph(escape(APP_NAME), title))
    story.append(Paragraph("Student Academic Report", sub))
    story.append(Spacer(1, 12))

    # Taarifa binafsi
    story.append(Paragraph("Student Information", h2))
    info = [
        ["Full Name", _p(student.get("full_name"), cell), "Reg No", _p(student.get("reg_no"), cell)],
        ["Programme", _p(student.get("programme_name"), cell), "Course", _p(student.get("course_name"), cell)],
        ["Year of Study", _p(student.get("year_of_study"), cell), "Email", _p(student.get("email") or "-", cell)],
        ["Phone", _p(student.get("phone") or "-", cell), "Date Issued", _p(date.today().strftime("%d %b %Y"), cell)],
    ]
    info_table = Table(info, colWidths=[3 * cm, 5.6 * cm, 3 * cm, 5.6 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5ccd3")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)

    # Matokeo
    story.append(Paragraph("Examination Results", h2))
    if marks_df is None or marks_df.empty:
        story.append(Paragraph("No marks have been recorded yet.", styles["Normal"]))
    else:
        df = marks_df.copy()
        df["score"] = df["score"].astype(float)
        df["max_score"] = df["max_score"].astype(float)
        df["percentage"] = (df["score"] / df["max_score"] * 100).round(2)
        df = df.sort_values(["course_name", "exam_date"], ascending=[True, True])

        rows = [["Course", "Exam", "Date", "Score", "Out of", "%", "Grade"]]
        for _, r in df.iterrows():
            exam_date = r["exam_date"].strftime("%d %b %Y") if hasattr(r["exam_date"], "strftime") and r["exam_date"] else "-"
            rows.append([
                _p(r["course_name"], cell), _p(r["exam_name"], cell), exam_date,
                f"{r['score']:g}", f"{r['max_score']:g}", f"{r['percentage']:.1f}",
                grade_from_percentage(r["percentage"]),
            ])
        t = Table(rows, colWidths=[4.4 * cm, 3.6 * cm, 2.4 * cm, 1.7 * cm, 1.7 * cm, 1.6 * cm, 1.6 * cm], repeatRows=1)
        t.setStyle(_table_style())
        t.setStyle(TableStyle([("ALIGN", (3, 0), (-1, -1), "CENTER")]))
        story.append(t)

        # Wastani kwa kila somo
        story.append(Paragraph("Summary per Course", h2))
        per_course = df.groupby("course_name")["percentage"].mean().round(2)
        srows = [["Course", "Average %", "Grade"]]
        for name, avg in per_course.items():
            srows.append([_p(name, cell), f"{avg:.1f}", grade_from_percentage(avg)])
        overall = df["percentage"].mean()
        srows.append(["Overall Average", f"{overall:.1f}", grade_from_percentage(overall)])
        st = Table(srows, colWidths=[9.5 * cm, 3.8 * cm, 3.8 * cm], repeatRows=1)
        st.setStyle(_table_style())
        st.setStyle(TableStyle([
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d6e4ea")),
        ]))
        story.append(st)

    # Mahudhurio
    story.append(Paragraph("Attendance Summary", h2))
    if att_summary_df is None or att_summary_df.empty:
        story.append(Paragraph("No attendance has been recorded yet.", styles["Normal"]))
    else:
        arows = [["Course", "Present", "Absent", "Total", "Attendance %"]]
        tp = ta = tt = 0
        for _, r in att_summary_df.iterrows():
            present, absent, total = int(r["present_count"]), int(r["absent_count"]), int(r["total_count"])
            tp, ta, tt = tp + present, ta + absent, tt + total
            pct = round(present / total * 100, 1) if total else 0
            arows.append([_p(r["course_name"], cell), present, absent, total, f"{pct}%"])
        overall_att = round(tp / tt * 100, 1) if tt else 0
        arows.append(["Overall", tp, ta, tt, f"{overall_att}%"])
        at = Table(arows, colWidths=[6.5 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.8 * cm], repeatRows=1)
        at.setStyle(_table_style())
        at.setStyle(TableStyle([
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d6e4ea")),
        ]))
        story.append(at)

    story.append(Spacer(1, 18))
    story.append(Paragraph(
        "Grading: A (70-100), B (60-69), C (50-59), D (40-49), F (below 40). "
        "This report was generated automatically by the system.",
        ParagraphStyle("f", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
    ))

    doc.build(story)
    return buffer.getvalue()