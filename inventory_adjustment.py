from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random

fake = Faker()

BUCKET_NAME = "dummy-dromos-documents"
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Inventory Adjustment & Shrinkage Reports"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_adjustment_report(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Inventory Adjustment / Shrinkage Report", styles["Title"]))
        elements.append(Spacer(1, 10))

        # Metadata
        metadata = [
            ["Report ID", f"ADJ-{fake.random_int(1000, 9999)}"],
            ["Warehouse", f"{fake.company()} Main Facility"],
            ["Prepared By", fake.name()],
            ["Date", fake.date_this_year().strftime("%Y-%m-%d")],
            ["Approved By", fake.name()],
            ["Adjustment Type", random.choice(["Shrinkage", "Damage", "Theft", "System Error", "Misplaced"])],
        ]
        table_meta = Table(metadata, colWidths=[130, 350])
        table_meta.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table_meta)
        elements.append(Spacer(1, 12))

        # Table header
        data = [["Item Code", "Description", "Expected Qty", "Actual Qty", "Variance", "Reason", "Remarks"]]

        reasons = ["Broken during transit", "Spoilage", "Theft", "Expired", "Data entry error"]
        for _ in range(random.randint(10, 20)):
            item_code = f"SKU-{fake.random_int(10000, 99999)}"
            desc = Paragraph(fake.bs().capitalize(), wrap_style)
            expected = random.randint(50, 500)
            variance = random.randint(-10, 0)
            actual = expected + variance
            reason = random.choice(reasons)
            remarks = Paragraph(fake.sentence(nb_words=8), wrap_style)

            data.append([
                item_code,
                desc,
                expected,
                actual,
                variance,
                reason,
                remarks
            ])

        table = Table(data, colWidths=[70, 110, 60, 60, 50, 80, 90])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 18))

        elements.append(Paragraph("Signature (Supervisor): ______________________", styles["Normal"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Comments:", styles["Normal"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(fake.paragraph(nb_sentences=3), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate and upload 150 reports ===
if __name__ == "__main__":
    for i in range(100):
        generate_adjustment_report(f"inventory_adjustment_report_{i+1}.pdf")
