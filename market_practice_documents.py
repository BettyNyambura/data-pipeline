from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from faker import Faker
from google.cloud import storage
import tempfile
from datetime import datetime
import random

fake = Faker()
BUCKET_NAME = "dummy-dromos-documents"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def build_and_upload_realistic_market_doc(filename):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionTitle", fontSize=13, leading=16, spaceAfter=10, spaceBefore=15, bold=True))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        today = datetime.today().strftime("%d %B %Y")
        report_id = f"MP-{fake.random_int(1000,9999)}-{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}"

        # HEADER
        elements.append(Paragraph("Market Practices Review Report", styles['Title']))
        elements.append(Paragraph(f"Report ID: {report_id}", styles['Normal']))
        elements.append(Paragraph(f"Date: {today}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Executive Summary
        summary_text = (
            f"This report provides an overview of the underwriting and sales practices of {fake.company()} "
            f"at its {fake.city()} branch. The review assessed compliance with internal policies and industry standards. "
            "Findings are based on sampled policy documentation, interviews with staff, and customer feedback."
        )
        elements.append(Paragraph("1. Executive Summary", styles["SectionTitle"]))
        elements.append(Paragraph(summary_text, styles["Normal"]))

        # Scope & Objectives
        scope = (
            "The objective of this review was to assess the consistency and regulatory compliance of day-to-day market practices, "
            "including quotation issuance, premium collection, policy documentation, and client onboarding processes."
        )
        elements.append(Paragraph("2. Scope & Objectives", styles["SectionTitle"]))
        elements.append(Paragraph(scope, styles["Normal"]))

        # Observations
        elements.append(Paragraph("3. Observations", styles["SectionTitle"]))
        for obs in [
            f"Use of non-standard forms was noted in {fake.city()} branch.",
            f"Multiple policy quotes lacked agent authorization signatures.",
            f"Inconsistent premium calculation methods observed in {fake.company_suffix()} products.",
            f"{fake.name()} was observed bypassing required pre-approval steps.",
        ]:
            elements.append(Paragraph(f"• {obs}", styles["Normal"]))

        # Compliance Assessment Table
        compliance_table = [["Category", "Status", "Notes"]]
        for cat in ["Policy Issuance", "Premium Collection", "Agent Conduct", "Client KYC", "Claims Advising"]:
            compliance_table.append([
                cat,
                fake.random_element(["Compliant", "Partially Compliant", "Non-Compliant"]),
                fake.sentence()
            ])
        table = Table(compliance_table, colWidths=[150, 120, 220])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("4. Regulatory Compliance", styles["SectionTitle"]))
        elements.append(table)

        # Recommendations
        recommendations = [
            "Standardize quote templates across all branches.",
            "Mandate refresher training on policy issuance guidelines.",
            "Introduce automated validation for premium calculations.",
            "Strengthen documentation checks before policy approval.",
        ]
        elements.append(Paragraph("5. Recommendations", styles["SectionTitle"]))
        for rec in recommendations:
            elements.append(Paragraph(f"✓ {rec}", styles["Normal"]))

        # Sign Off
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Prepared by:", styles["Normal"]))
        elements.append(Paragraph(f"{fake.name()}, Regional Auditor", styles["Normal"]))
        elements.append(Paragraph("Approved by:", styles["Normal"]))
        elements.append(Paragraph(f"{fake.name()}, Compliance Manager", styles["Normal"]))

        doc.build(elements)

        # Upload
        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"Insurance/Claims/Market Practice Documents/{filename}"
        )

# === Generate and upload 10 documents ===
for i in range(200):
    file_name = f"market_practice_report_{i+1}.pdf"
    build_and_upload_realistic_market_doc(file_name)
