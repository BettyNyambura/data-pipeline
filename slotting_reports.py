from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
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
GCS_PATH = "Logistics Document Inventory (High‑Volume, High‑Velocity)/Warehouse & Inventory/Slotting & Layout Analysis Reports"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_slotting_layout_report(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Slotting & Layout Analysis Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Report Metadata
        meta = [
            ["Warehouse", fake.company()],
            ["Report ID", f"SLOT-{random.randint(1000, 9999)}"],
            ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Analyst", fake.name()],
            ["Zone Analyzed", fake.random_element(["Zone A", "Bulk Storage", "Fast Pick Area", "Receiving Dock"])],
        ]
        meta_table = Table(meta, colWidths=[150, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # Slotting Table
        slot_data = [["Item Code", "Description", "Current Slot", "Suggested Slot", "Turns/Month", "Pick Freq", "Reason for Change"]]
        for _ in range(random.randint(12, 20)):
            code = f"SKU-{random.randint(1000,9999)}"
            desc = Paragraph(fake.catch_phrase(), wrap_style)
            curr_slot = f"{random.choice(['A', 'B', 'C'])}-{random.randint(1,20)}"
            sugg_slot = f"{random.choice(['A', 'B', 'C'])}-{random.randint(1,20)}"
            turns = random.randint(1, 20)
            freq = fake.random_element(["High", "Medium", "Low"])
            reason = Paragraph(fake.sentence(nb_words=6), wrap_style)
            slot_data.append([code, desc, curr_slot, sugg_slot, turns, freq, reason])

        slot_table = Table(slot_data, colWidths=[60, 140, 70, 70, 60, 60, 100])
        slot_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(slot_table)
        elements.append(Spacer(1, 20))

        # Layout Summary
        elements.append(Paragraph("Layout Notes", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=4), styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Recommendations", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=3), styles["Normal"]))

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{GCS_PATH}/{filename}")

# === Generate 150 reports ===
if __name__ == "__main__":
    for i in range(1):
        generate_slotting_layout_report(f"slotting_layout_report_{i+1}.pdf")
