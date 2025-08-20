from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random
from datetime import datetime

fake = Faker()
BUCKET_NAME = "dummy-dromos-documents"
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Goods Received Notes (GRN)"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_grn(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Goods Received Note (GRN)", styles["Title"]))
        elements.append(Spacer(1, 12))

        grn_number = f"GRN-{fake.random_int(100000, 999999)}"
        date_received = fake.date_this_year().strftime("%Y-%m-%d")
        warehouse = fake.company() + " Warehouse"
        supplier = fake.company()
        po_number = f"PO-{fake.random_int(1000, 9999)}"

        metadata = [
            ["GRN Number:", grn_number],
            ["Date Received:", date_received],
            ["Warehouse Location:", warehouse],
            ["Supplier:", supplier],
            ["PO Number:", po_number]
        ]
        meta_table = Table(metadata, colWidths=[130, 300])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # Items received
        elements.append(Paragraph("Items Received", styles["Heading2"]))
        item_data = [["Item Description", "Item Code", "Qty Ordered", "Qty Received", "Unit", "Remarks"]]
        for _ in range(random.randint(3, 6)):
            desc = fake.bs().title()
            code = f"ITEM-{fake.random_int(1000, 9999)}"
            qty_ordered = random.randint(10, 100)
            qty_received = qty_ordered - random.randint(0, 5)
            unit = fake.random_element(["PCS", "CTN", "KG", "LTR"])
            remark = fake.random_element(["OK", "Damaged", "Short", "Surplus"])
            item_data.append([desc, code, qty_ordered, qty_received, unit, remark])

        item_table = Table(item_data, colWidths=[140, 80, 80, 80, 50, 80])
        item_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(item_table)
        elements.append(Spacer(1, 18))

        elements.append(Paragraph("Received By: ____________________        Date: ____________", styles["Normal"]))
        elements.append(Paragraph("Verified By: _____________________       Signature: ________", styles["Normal"]))

        doc.build(elements)

        # Upload to GCS
        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{GCS_PATH}/{filename}"
        )

# === MAIN ===
if __name__ == "__main__":
    for i in range(300):
        print(f"📄 Generating GRN {i+1}")
        generate_grn(f"grn_{i+1}.pdf")
