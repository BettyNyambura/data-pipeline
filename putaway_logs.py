from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random
import os

fake = Faker()
BUCKET_NAME = "dummy-dromos-documents"
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Put‑away & Location Assignment Logs"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_putaway_log(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Put‑away & Location Assignment Log", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Metadata
        log_id = f"PA-{fake.random_int(1000, 9999)}"
        warehouse = fake.company() + " Warehouse"
        supervisor = fake.name()
        date = fake.date_this_year().strftime("%Y-%m-%d")

        metadata = [
            ["Log ID", log_id],
            ["Warehouse", warehouse],
            ["Supervisor", supervisor],
            ["Date", date]
        ]
        meta_table = Table(metadata, colWidths=[120, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey)
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # Table Header
        data = [["Item Code", "Description", "Quantity", "Storage Zone", "Bin/Location", "Put-away Time"]]
        for _ in range(random.randint(6, 12)):
            code = f"SKU-{fake.random_int(10000, 99999)}"
            desc = fake.word().capitalize() + " - " + fake.color_name()
            qty = random.randint(5, 100)
            zone = random.choice(["A", "B", "C", "D"]) + str(random.randint(1, 5))
            location = f"{zone}-{random.randint(100, 999)}"
            time = fake.time(pattern="%H:%M")
            data.append([code, desc, qty, zone, location, time])

        table = Table(data, colWidths=[80, 140, 60, 70, 100, 70])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table)

        doc.build(elements)

        # Upload
        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{GCS_PATH}/{filename}"
        )

# === Generate and upload 150 logs ===
if __name__ == "__main__":
    for i in range(300):
        file_name = f"putaway_log_{i+1}.pdf"
        generate_putaway_log(file_name)
