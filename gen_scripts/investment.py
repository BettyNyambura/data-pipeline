from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
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
SUBTYPES = ["Share Certificate", "Investment Report", "Stock Purchase Agreement"]

# === Upload Function ===
def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

# === Document Generators ===
def generate_share_certificate(style):
    holder = fake.name()
    company = fake.company()
    shares = random.randint(100, 10000)
    certificate_id = fake.uuid4()
    return [
        Paragraph("Share Certificate", style["Title"]),
        Spacer(1, 12),
        Paragraph(f"This certifies that <b>{holder}</b> is the registered owner of <b>{shares} ordinary shares</b> in <b>{company}</b>.", style["Normal"]),
        Spacer(1, 12),
        Paragraph(f"Certificate ID: {certificate_id}", style["Normal"]),
        Paragraph(f"Issued Date: {datetime.now().strftime('%Y-%m-%d')}", style["Normal"]),
        Spacer(1, 24),
        Paragraph("Authorized Signatory: ___________________________", style["Normal"]),
        Paragraph("Company Seal: _________________________________", style["Normal"]),
    ]

def generate_investment_report(style):
    rows = [["Investment", "Amount", "Return (%)", "Status"]]
    for _ in range(random.randint(5, 8)):
        rows.append([
            fake.company(),
            f"${random.randint(5000, 500000):,}",
            f"{round(random.uniform(2, 15), 2)}%",
            random.choice(["Active", "Exited", "Pending"])
        ])
    return [
        Paragraph("Quarterly Investment Report", style["Title"]),
        Spacer(1, 12),
        Paragraph(f"Report Prepared For: {fake.name()}", style["Normal"]),
        Paragraph(f"Prepared By: {fake.company()}", style["Normal"]),
        Spacer(1, 12),
        Table(rows, colWidths=[200, 100, 100, 100], style=TableStyle([
            ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ])),
        Spacer(1, 12),
        Paragraph("Notes:", style["Heading2"]),
        Paragraph(fake.paragraph(nb_sentences=4), style["Normal"])
    ]

def generate_stock_purchase_agreement(style):
    buyer = fake.name()
    seller = fake.name()
    shares = random.randint(100, 1000)
    price = round(random.uniform(10, 100), 2)
    total = f"${shares * price:,.2f}"
    return [
        Paragraph("Stock Purchase Agreement", style["Title"]),
        Spacer(1, 12),
        Paragraph(f"This agreement is made on <b>{datetime.now().strftime('%B %d, %Y')}</b> between <b>{seller}</b> (the “Seller”) and <b>{buyer}</b> (the “Buyer”).", style["Normal"]),
        Spacer(1, 12),
        Paragraph(f"The Seller agrees to sell <b>{shares}</b> shares at <b>${price}</b> per share, totaling <b>{total}</b>.", style["Normal"]),
        Spacer(1, 12),
        Paragraph("Both parties acknowledge the terms and agree to comply with all governing regulations.", style["Normal"]),
        Spacer(1, 24),
        Paragraph("Seller Signature: ______________________", style["Normal"]),
        Paragraph("Buyer Signature: ______________________", style["Normal"]),
    ]

# === Main Document Builder ===
def generate_investment_document_file(filename):
    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    subtype = random.choice(SUBTYPES)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        elements = []

        # Metadata
        meta = [
            ["Document Type", subtype],
            ["Entity", fake.company()],
            ["Prepared For", fake.name()],
            ["Date", datetime.now().strftime("%Y-%m-%d")],
        ]
        meta_table = Table(meta, colWidths=[150, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 16))

        # Subtype Content
        if subtype == "Share Certificate":
            elements += generate_share_certificate(styles)
        elif subtype == "Investment Report":
            elements += generate_investment_report(styles)
        elif subtype == "Stock Purchase Agreement":
            elements += generate_stock_purchase_agreement(styles)

        doc.build(elements)

        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{CATEGORY}/Investment_Documents/{subtype.replace(' ', '_')}/{filename}"
        )

# === Run Batch Generation ===
if __name__ == "__main__":
    for i in range(300):
        generate_investment_document_file(f"investment_doc_{i+1}.pdf")
