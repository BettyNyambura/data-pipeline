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
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Bin Slot Transfer Documents"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_bin_transfer_doc(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Bin/Slot Transfer Document", styles["Title"]))
        elements.append(Spacer(1, 12))

        metadata = [
            ["Transfer ID", f"TRF-{fake.random_int(1000, 9999)}"],
            ["Warehouse", fake.company()],
            ["Operator", fake.name()],
            ["Date", fake.date_time_this_year().strftime("%Y-%m-%d %H:%M")],
            ["Approved By", fake.name()],
        ]
        table_meta = Table(metadata, colWidths=[130, 350])
        table_meta.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table_meta)
        elements.append(Spacer(1, 12))

        data = [["Item Code", "Description", "Quantity", "From Bin", "To Bin", "Timestamp", "Remarks"]]

        for _ in range(random.randint(8, 15)):
            item_code = f"SKU-{fake.random_int(10000, 99999)}"
            desc = Paragraph(fake.word().capitalize() + " - " + fake.bs(), wrap_style)
            qty = random.randint(5, 100)
            from_bin = f"A{random.randint(1, 9)}-B{random.randint(10, 50)}"
            to_bin = f"B{random.randint(1, 9)}-C{random.randint(10, 50)}"
            time = (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M")
            remarks = Paragraph(fake.sentence(nb_words=5), wrap_style)

            data.append([item_code, desc, qty, from_bin, to_bin, time, remarks])

        table = Table(data, colWidths=[70, 130, 50, 60, 60, 80, 80])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("Signature (Warehouse Supervisor): ______________________", styles["Normal"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Notes:", styles["Normal"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=2), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate and upload 150 documents ===
if __name__ == "__main__":
    for i in range(100):
        generate_bin_transfer_doc(f"bin_slot_transfer_{i+1}.pdf")
