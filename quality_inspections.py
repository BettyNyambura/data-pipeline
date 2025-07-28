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
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Quality Inspection Checklists"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_quality_checklist(filename):
    styles = getSampleStyleSheet()
    wrap = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Quality Inspection Checklist", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Header info
        header = [
            ["Inspection Date", datetime.now().strftime("%Y-%m-%d")],
            ["Inspector Name", fake.name()],
            ["Batch/Shipment No.", f"BATCH-{random.randint(1000,9999)}"],
            ["Supplier", fake.company()],
        ]
        t_header = Table(header, colWidths=[140, 320])
        t_header.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 12))

        # Inspection Table
        data = [["Item Code", "Item Description", "Criteria", "Pass/Fail", "Remarks"]]
        for _ in range(random.randint(15, 25)):
            item_code = f"ITEM-{random.randint(10000,99999)}"
            item_desc = Paragraph(fake.catch_phrase(), wrap)
            criteria = random.choice(["No visible damage", "Correct labeling", "Right quantity", "Temperature check", "Expiry check"])
            result = random.choice(["Pass", "Fail"])
            remark = Paragraph(fake.sentence(nb_words=6) if result == "Fail" else "-", wrap)
            data.append([item_code, item_desc, criteria, result, remark])

        table = Table(data, colWidths=[70, 130, 120, 60, 110])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
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

# === Generate 150 reports ===
if __name__ == "__main__":
    for i in range(200):
        generate_quality_checklist(f"quality_inspection_checklist_{i+1}.pdf")
