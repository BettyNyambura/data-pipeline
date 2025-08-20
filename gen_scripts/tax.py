from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random
from datetime import datetime

# === Setup ===
fake = Faker()
BUCKET_NAME = "dummy-dromos-documents"
CATEGORY = "Financial_Documents"
SUBTYPES = ["Tax Return", "Withholding Certificate", "VAT Return"]

# === Upload Function ===
def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

# === Generate Document ===
def generate_tax_document_file(filename):
    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    subtype = random.choice(SUBTYPES)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        elements = []

        # === Title ===
        elements.append(Paragraph(f"{subtype}", styles["Title"]))
        elements.append(Spacer(1, 12))

        # === Metadata ===
        meta = [
            ["Entity Name", fake.company()],
            ["Document Type", subtype],
            ["Tax Year", str(fake.year())],
            ["Prepared By", fake.name()],
        ]
        meta_table = Table(meta, colWidths=[150, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 16))

        # === Subtype Logic ===
        if subtype == "Tax Return":
            elements += generate_tax_return(normal)
        elif subtype == "Withholding Certificate":
            elements += generate_withholding_certificate(normal)
        elif subtype == "VAT Return":
            elements += generate_vat_return(normal)

        # === Summary ===
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Remarks / Notes", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=4), normal))

        doc.build(elements)

        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{CATEGORY}/Tax_Documents/{subtype.replace(' ', '_')}/{filename}"
        )

# === Subtype Content Builders ===
def generate_tax_return(style):
    rows = [
        ["Income", random_amount()],
        ["Deductions", f"-{random_amount()}"],
        ["Taxable Income", ""],
        ["Tax Rate", "25%"],
        ["Calculated Tax", ""],
        ["Tax Credits", f"-{random_amount()}"],
        ["Tax Payable", ""],
    ]
    return [
        Paragraph("Tax Return Summary", style),
        tax_table(rows)
    ]

def generate_withholding_certificate(style):
    rows = [
        ["Employee Name", fake.name()],
        ["Employee ID", fake.uuid4()],
        ["Gross Pay", random_amount()],
        ["Tax Withheld", f"-{random_amount()}"],
        ["Employer Name", fake.company()],
        ["Period Covered", f"{fake.date_this_year()} - {fake.date_this_year()}"],
        ["Issued Date", datetime.now().strftime("%Y-%m-%d")],
    ]
    return [
        Paragraph("Withholding Certificate Details", style),
        tax_table(rows)
    ]

def generate_vat_return(style):
    rows = [
        ["Total Sales (Excl. VAT)", random_amount()],
        ["VAT Collected (Output Tax)", random_amount()],
        ["Purchases (Excl. VAT)", random_amount()],
        ["VAT Paid (Input Tax)", random_amount()],
        ["Net VAT Payable", ""],
        ["Filing Period", fake.month_name() + " " + str(fake.year())],
    ]
    return [
        Paragraph("VAT Return Overview", style),
        tax_table(rows)
    ]

# === Helpers ===
def random_amount():
    return f"${round(random.uniform(500, 100000), 2):,.2f}"

def tax_table(data):
    t = Table(data, colWidths=[250, 200])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightyellow),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ]))
    return t

# === Main Runner ===
if __name__ == "__main__":
    for i in range(300):
        generate_tax_document_file(f"tax_document_{i+1}.pdf")
