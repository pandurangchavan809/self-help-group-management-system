from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch

import matplotlib.pyplot as plt
import tempfile
import os
from datetime import datetime

# MAIN PDF GENERATOR (FINAL)

def generate_shg_report(
    file_path,
    shg_name,
    village,
    period_from,
    period_to,
    summary,
    member_summary,
    loan_summary
):
    """
    Generates a complete SHG PDF report.
    """

    # PDF SETUP
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []

    # HEADER
    elements.append(Paragraph(
        "<b>MAHILA BACHAT GAT REPORT</b>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"<b>{shg_name.upper()} ({village})</b>",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        f"Period: {period_from} – {period_to}<br/>"
        f"Generated on: {datetime.today().strftime('%d %b %Y')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    # SUMMARY TABLE
    elements.append(Paragraph("<b>Financial Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    summary_table = Table(
        [
            ["Total Savings", f"₹ {summary['savings']}"],
            ["Total Loan Given", f"₹ {summary['loan']}"],
            ["Available Cash", f"₹ {summary['cash']}"],
        ],
        colWidths=[3.5 * inch, 2 * inch]
    )

    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONT", (0, 0), (-1, -1), "Helvetica"),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 24))

    # PIE CHART
    elements.append(Paragraph("<b>Financial Overview</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        [summary["savings"], summary["loan"]],
        labels=["Savings", "Loans"],
        autopct="%1.0f%%",
        startangle=140
    )
    ax.axis("equal")

    tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp_img.name, bbox_inches="tight")
    plt.close(fig)

    elements.append(Image(tmp_img.name, width=3.5 * inch, height=3.5 * inch))
    elements.append(Spacer(1, 24))

    # MEMBER SUMMARY
    elements.append(Paragraph("<b>Member-wise Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    member_table_data = [["Member", "Deposit", "Loan", "Repaid", "Balance"]]
    for m in member_summary:
        member_table_data.append([
            m["name"],
            f"₹ {m['deposit']}",
            f"₹ {m['loan']}",
            f"₹ {m['repaid']}",
            f"₹ {m['balance']}"
        ])

    member_table = Table(member_table_data, repeatRows=1)
    member_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(member_table)
    elements.append(Spacer(1, 24))

    # LOAN SUMMARY
    elements.append(Paragraph("<b>Loan Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    loan_table_data = [["Member", "Amount", "Interest Paid", "Status"]]
    for l in loan_summary:
        loan_table_data.append([
            l["name"],
            f"₹ {l['amount']}",
            f"₹ {l['interest']}",
            l["status"].capitalize()
        ])

    loan_table = Table(loan_table_data, repeatRows=1)
    loan_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(loan_table)
    elements.append(Spacer(1, 30))

    # FOOTER
    elements.append(Paragraph(
        "<i>This report is system generated. "
        "No data can be altered manually.</i>",
        styles["Normal"]
    ))

    # BUILD
    doc.build(elements)

    # cleanup temp image
    if os.path.exists(tmp_img.name):
        os.unlink(tmp_img.name)
