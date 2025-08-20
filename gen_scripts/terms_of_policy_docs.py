from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from faker import Faker
from google.cloud import storage
import tempfile
import random
from datetime import datetime, timedelta

fake = Faker()
BUCKET_NAME = "dummy-dromos-documents"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def build_and_upload_terms_of_policy(filename):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Section", fontSize=12, spaceBefore=12, spaceAfter=6, leading=15, bold=True))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        today = datetime.today().strftime("%d %B %Y")
        policy_number = f"POL-{fake.random_int(100000,999999)}"

        # Header
        elements.append(Paragraph("Terms of Insurance Policy", styles["Title"]))
        elements.append(Paragraph(f"Policy No: {policy_number}", styles["Normal"]))
        elements.append(Paragraph(f"Issue Date: {today}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Section 1 – Policyholder Details
        elements.append(Paragraph("1. Policyholder Information", styles["Section"]))
        holder_info = [
            ["Full Name", fake.name()],
            ["Date of Birth", fake.date_of_birth(minimum_age=21, maximum_age=65).strftime("%Y-%m-%d")],
            ["Address", fake.address().replace("\n", ", ")],
            ["Phone Number", fake.phone_number()],
            ["Email", fake.email()],
        ]
        table1 = Table(holder_info, colWidths=[150, 300])
        table1.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ]))
        elements.append(table1)

        # Section 2 – Policy Coverage
        elements.append(Paragraph("2. Policy Coverage", styles["Section"]))
        policy_type = fake.random_element(["Life Insurance", "Health Cover", "Motor Cover", "Property Protection"])
        start_date = datetime.today()
        end_date = start_date + timedelta(days=365 * random.randint(1, 5))
        coverage = f"""
        This {policy_type} policy provides coverage against financial risks related to covered incidents as defined 
        under the general policy agreement. The policy remains effective from <b>{start_date.strftime('%d %b %Y')}</b> 
        to <b>{end_date.strftime('%d %b %Y')}</b>, subject to payment of premiums and compliance with terms.
        """
        elements.append(Paragraph(coverage, styles["Normal"]))

        # Section 3 – Premium & Payment Terms
        elements.append(Paragraph("3. Premium and Payment Terms", styles["Section"]))
        premium = f"KES {random.randint(5_000, 50_000)}"
        frequency = fake.random_element(["Monthly", "Quarterly", "Annually"])
        payment_clause = f"""
        The policyholder agrees to pay a premium of <b>{premium}</b> on a <b>{frequency}</b> basis. Failure to make payments
        within the defined grace period (15 days) shall result in policy suspension or termination.
        """
        elements.append(Paragraph(payment_clause, styles["Normal"]))

        # Section 4 – Exclusions
        elements.append(Paragraph("4. Policy Exclusions", styles["Section"]))
        exclusions = [
            "Intentional self-harm or suicide within the first year of the policy.",
            "Losses incurred during illegal activities.",
            "Claims arising from undisclosed pre-existing medical conditions.",
            "Natural disasters not covered by optional riders.",
            "War, riots, or civil commotion."
        ]
        for ex in exclusions:
            elements.append(Paragraph(f"• {ex}", styles["Normal"]))

        # Section 5 – Cancellation & Refund
        elements.append(Paragraph("5. Cancellation & Refund", styles["Section"]))
        cancel_text = """
        The policyholder may cancel this policy by providing a 30-day written notice. Refunds will be issued 
        based on the pro-rated premium amount after deducting administrative charges.
        """
        elements.append(Paragraph(cancel_text, styles["Normal"]))

        # Section 6 – Sign-Off
        elements.append(Paragraph("6. Acknowledgement", styles["Section"]))
        signoff = """
        By accepting this document, the policyholder agrees to all terms, coverage conditions, and exclusions 
        detailed herein. This document is to be retained with the master policy.
        """
        elements.append(Paragraph(signoff, styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Signature of Policyholder: ______________________", styles["Normal"]))
        elements.append(Paragraph(f"Authorized by: {fake.name()}, Underwriting Officer", styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"Insurance/Claims/Terms of Policy/{filename}"
        )

# === Generate and upload 10 documents ===
for i in range(300):
    file_name = f"terms_of_policy_{i+1}.pdf"
    build_and_upload_terms_of_policy(file_name)
