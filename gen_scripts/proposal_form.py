from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from faker import Faker
from google.cloud import storage
import os
import tempfile

fake = Faker()

# Set your target GCS bucket
BUCKET_NAME = "dummy-dromos-documents"  # <-- change this

# Upload to GCS
def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded to GCS: gs://{bucket_name}/{destination_blob_name}")

# Build the proposal form and upload
def build_and_upload_proposal_form(filename):
    styles = getSampleStyleSheet()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []

        elements.append(Paragraph("Insurance Proposal Form", styles['Title']))
        elements.append(Spacer(1, 12))

        # Personal details
        personal_table = [
            ["Name", fake.name()],
            ["Date of Birth", fake.date_of_birth().strftime("%Y-%m-%d")],
            ["Gender", fake.random_element(["Male", "Female"])],
            ["Marital Status", fake.random_element(["Single", "Married", "Divorced"])],
            ["Mobile Number", fake.phone_number()],
            ["Email", fake.email()],
            ["ID/Passport", fake.ssn()],
            ["Address", fake.address().replace("\n", ", ")],
        ]
        elements.append(Paragraph("Personal Details", styles['Heading2']))
        t = Table(personal_table, colWidths=[120, 300])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        # Policy Details
        policy_table = [
            ["Policy Type", fake.random_element(["Life", "Health", "Vehicle", "Property"])],
            ["Option", fake.random_element(["Basic", "Standard", "Premium"])],
            ["Term (Years)", fake.random_int(1, 10)],
            ["Sum Assured", f"KES {fake.random_int(100000, 5000000)}"],
            ["Premium", f"KES {fake.random_int(1000, 100000)}"],
            ["Payment Frequency", fake.random_element(["Monthly", "Quarterly", "Annually"])],
        ]
        elements.append(Paragraph("Policy Details", styles['Heading2']))
        t2 = Table(policy_table, colWidths=[150, 270])
        t2.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 12))

        # Beneficiaries Table
        elements.append(Paragraph("Beneficiaries", styles['Heading2']))
        ben_table_data = [["Name", "Relationship", "DOB", "% Share", "Contact"]]
        for _ in range(3):
            ben_table_data.append([
                fake.name(),
                fake.random_element(["Spouse", "Child", "Sibling"]),
                fake.date_of_birth().strftime("%Y-%m-%d"),
                f"{fake.random_element([50, 30, 20])}%",
                fake.phone_number()
            ])
        t3 = Table(ben_table_data, colWidths=[120, 100, 90, 60, 100])
        t3.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t3)

        elements.append(Spacer(1, 18))
        elements.append(Paragraph("Signature: _______________________      Date: ________________", styles['Normal']))

        doc.build(elements)

        # Upload the PDF file to GCS
        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"Insurance/Claims/Proposal form/{filename}"
        )

# === Generate and upload 3 forms ===
for i in range(150):
    file_name = f"proposal_form_{i+1}.pdf"
    build_and_upload_proposal_form(file_name)
