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
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/On‑hand vs Allocated Stock Reports"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_stock_allocation_report(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("On‑hand vs Allocated Stock Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Report Header
        meta = [
            ["Warehouse", fake.company()],
            ["Report Date", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Prepared By", fake.name()],
            ["System Ref ID", f"ALLOC-{random.randint(10000, 99999)}"],
        ]
        meta_table = Table(meta, colWidths=[150, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # Stock Table
        data = [["Item Code", "Description", "Location", "On‑hand Qty", "Allocated Qty", "Available Qty", "Remarks"]]
        for _ in range(random.randint(20, 35)):
            code = f"SKU-{random.randint(10000, 99999)}"
            desc = Paragraph(fake.bs().capitalize(), wrap_style)
            location = f"{random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1,20)}"
            on_hand = random.randint(100, 500)
            allocated = random.randint(0, on_hand)
            available = on_hand - allocated
            remarks = Paragraph(fake.sentence(nb_words=6), wrap_style)
            data.append([code, desc, location, on_hand, allocated, available, remarks])

        table = Table(data, colWidths=[70, 130, 60, 60, 60, 60, 90])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table)

        # Summary
        elements.append(Spacer(1, 18))
        elements.append(Paragraph("Summary & Notes", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=4), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate 150 reports ===
if __name__ == "__main__":
    for i in range(150):
        generate_stock_allocation_report(f"onhand_vs_allocated_report_{i+1}.pdf")
