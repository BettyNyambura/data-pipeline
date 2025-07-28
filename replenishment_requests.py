from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random
from datetime import datetime, timedelta

fake = Faker()

BUCKET_NAME = "dummy-dromos-documents"
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Replenishment Requests"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_replenishment_request(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        # Header
        elements.append(Paragraph("Replenishment Request", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Metadata
        metadata = [
            ["Request ID", f"RR-{fake.random_int(10000,99999)}"],
            ["Requested By", fake.name()],
            ["Department", fake.random_element(["Retail Floor", "Pharmacy", "Main Warehouse", "Production"])],
            ["Date", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Expected Delivery", (datetime.now() + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d")],
        ]
        table_meta = Table(metadata, colWidths=[150, 330])
        table_meta.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(table_meta)
        elements.append(Spacer(1, 12))

        # Line Items
        data = [["Item Code", "Description", "Requested Qty", "Unit", "Current Stock", "Suggested Supplier", "Remarks"]]
        for _ in range(random.randint(6, 12)):
            item_code = f"ITM-{fake.random_int(1000,9999)}"
            desc = Paragraph(fake.catch_phrase(), wrap_style)
            qty = random.randint(10, 100)
            unit = fake.random_element(["pcs", "boxes", "kg", "liters"])
            stock = random.randint(0, 30)
            supplier = fake.company()
            remarks = Paragraph(fake.sentence(nb_words=5), wrap_style)

            data.append([item_code, desc, qty, unit, stock, supplier, remarks])

        table = Table(data, colWidths=[70, 130, 60, 40, 60, 100, 90])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(table)

        # Footer
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Authorized by: ________________________", styles["Normal"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Comments:", styles["Normal"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=2), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate 150 replenishment requests ===
if __name__ == "__main__":
    for i in range(120):
        generate_replenishment_request(f"replenishment_request_{i+1}.pdf")
