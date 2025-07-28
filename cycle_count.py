from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random
import os

fake = Faker()

BUCKET_NAME = "dummy-dromos-documents"
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Cycle‑Count & Stock‑take Records"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_cycle_count_record(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Cycle‑Count & Stock‑take Record", styles["Title"]))
        elements.append(Spacer(1, 10))

        # Metadata
        metadata = [
            ["Stock-take ID", f"ST-{fake.random_int(10000,99999)}"],
            ["Warehouse", f"{fake.company()} Regional DC"],
            ["Supervisor", fake.name()],
            ["Date of Count", fake.date_this_year().strftime("%Y-%m-%d")],
            ["Count Type", random.choice(["Cycle Count", "Full Inventory", "Spot Check"])],
            ["Shift", random.choice(["Morning", "Afternoon", "Night"])],
        ]
        table_meta = Table(metadata, colWidths=[130, 350])
        table_meta.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table_meta)
        elements.append(Spacer(1, 12))

        # Inventory Table
        data = [[
            "Category", "Item Code", "Item Description",
            "System Qty", "Counted Qty", "Variance", "Location", "Remarks"
        ]]

        categories = ["Electronics", "Food & Beverage", "Stationery", "Hardware", "Apparel"]
        for _ in range(random.randint(20, 35)):
            category = random.choice(categories)
            item_code = f"SKU-{fake.random_int(10000,99999)}"
            description = Paragraph(f"{fake.word().capitalize()} - {fake.color_name()}", wrap_style)
            system_qty = random.randint(10, 200)
            counted_qty = system_qty + random.randint(-10, 10)
            variance = counted_qty - system_qty
            location = f"Aisle {random.randint(1, 10)} - Bin {random.randint(100, 999)}"
            remark_text = "OK" if variance == 0 else ("Over" if variance > 0 else "Short")
            remarks = Paragraph(remark_text, wrap_style)
            data.append([
                category, item_code, description,
                system_qty, counted_qty, variance,
                location, remarks
            ])

        inventory_table = Table(data, colWidths=[60, 60, 110, 50, 50, 50, 75, 65])
        inventory_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (3,1), (-3,-1), 'CENTER')
        ]))
        elements.append(inventory_table)
        elements.append(Spacer(1, 18))

        # Footer/Notes
        elements.append(Paragraph("Verified by: ____________________________", styles["Normal"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Comments:", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(fake.paragraph(nb_sentences=3), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate and upload 150 records ===
if __name__ == "__main__":
    for i in range(300):
        generate_cycle_count_record(f"cycle_count_record_{i+1}.pdf")
