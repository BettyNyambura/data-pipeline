from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random
from datetime import datetime

fake = Faker()

BUCKET_NAME = "dummy-dromos-documents"
GCS_PATH = "Logistics Document Inventory (High-Volume, High-Velocity)/Warehouse & Inventory/Non-Conformance or Damage Reports"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_damage_report(filename):
    styles = getSampleStyleSheet()
    wrap = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Non‑Conformance / Damage Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Header Info
        header = [
            ["Report Date", datetime.now().strftime("%Y-%m-%d")],
            ["Reported By", fake.name()],
            ["Department", random.choice(["Receiving", "Inventory", "Shipping", "Quality Control"])],
            ["Reference No.", f"NC-{random.randint(10000,99999)}"]
        ]
        t_header = Table(header, colWidths=[130, 320])
        t_header.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 12))

        # Damaged Items Table
        data = [["Item Code", "Description", "Issue", "Severity", "Qty Affected", "Action Required"]]
        issues = ["Physical Damage", "Quantity Mismatch", "Packaging Tear", "Expired Item", "Incorrect Label"]
        actions = ["Return to Supplier", "Repack", "Dispose", "Re-inspect", "Hold in Quarantine"]

        for _ in range(random.randint(5, 12)):
            row = [
                f"ITEM-{random.randint(10000,99999)}",
                Paragraph(fake.catch_phrase(), wrap),
                random.choice(issues),
                random.choice(["Low", "Medium", "High"]),
                random.randint(1, 20),
                random.choice(actions)
            ]
            data.append(row)

        table = Table(data, colWidths=[70, 130, 90, 60, 60, 100])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.orange),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table)

        # Notes
        elements.append(Spacer(1, 18))
        elements.append(Paragraph("Inspector Notes", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=3), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate 150 Reports ===
if __name__ == "__main__":
    for i in range(250):
        generate_damage_report(f"non_conformance_report_{i+1}.pdf")
