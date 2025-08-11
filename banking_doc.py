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
SUBTYPES = ["Bank Statement", "Loan Agreement", "Credit Facility Letter"]

# === Upload Function ===
def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

# === Generate Document ===
def generate_banking_loan_document_file(filename):
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
            ["Client Name", fake.name()],
            ["Document Type", subtype],
            ["Bank/Institution", fake.company()],
            ["Issued Date", datetime.now().strftime("%Y-%m-%d")],
        ]
        meta_table = Table(meta, colWidths=[150, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 16))

        # === Subtype Logic ===
        if subtype == "Bank Statement":
            elements += generate_bank_statement(normal)
        elif subtype == "Loan Agreement":
            elements += generate_loan_agreement(normal)
        elif subtype == "Credit Facility Letter":
            elements += generate_credit_facility_letter(normal)

        # === Summary ===
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Remarks / Notes", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=4), normal))

        doc.build(elements)

        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{CATEGORY}/Banking_Loan_Documents/{subtype.replace(' ', '_')}/{filename}"
        )

# === Subtype Content Builders ===
def generate_bank_statement(style):
    rows = [["Date", "Description", "Amount", "Balance"]]
    balance = 1000.00
    for _ in range(10):
        amount = round(random.uniform(-500, 1500), 2)
        balance += amount
        rows.append([
            fake.date_this_year().strftime("%Y-%m-%d"),
            fake.bs().capitalize(),
            f"${amount:,.2f}",
            f"${balance:,.2f}"
        ])
    return [
        Paragraph("Transaction History", style),
        bank_table(rows)
    ]

def generate_loan_agreement(style):
    rows = [
        ["Loan Amount", random_amount()],
        ["Interest Rate", f"{round(random.uniform(3, 10), 2)}%"],
        ["Term", f"{random.choice([12, 24, 36, 60])} months"],
        ["Monthly Payment", random_amount()],
        ["Start Date", fake.date_this_year().strftime("%Y-%m-%d")],
        ["End Date", fake.date_this_year().strftime("%Y-%m-%d")],
        ["Collateral", fake.word().capitalize()],
    ]
    return [
        Paragraph("Loan Agreement Details", style),
        loan_table(rows)
    ]

def generate_credit_facility_letter(style):
    rows = [
        ["Facility Type", random.choice(["Overdraft", "Term Loan", "Revolving Credit"])],
        ["Approved Limit", random_amount()],
        ["Interest Rate", f"{round(random.uniform(4, 12), 2)}%"],
        ["Facility Tenure", f"{random.choice([6, 12, 24, 36])} months"],
        ["Repayment Terms", "Monthly Installments"],
        ["Review Date", fake.future_date().strftime("%Y-%m-%d")],
    ]
    return [
        Paragraph("Credit Facility Summary", style),
        facility_table(rows)
    ]

# === Helpers ===
def random_amount():
    return f"${round(random.uniform(5000, 100000), 2):,.2f}"

def bank_table(data):
    t = Table(data, colWidths=[100, 220, 80, 80])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
    ]))
    return t

def loan_table(data):
    t = Table(data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ]))
    return t

def facility_table(data):
    t = Table(data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.beige),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ]))
    return t

# === Main Runner ===
if __name__ == "__main__":
    for i in range(300):
        generate_banking_loan_document_file(f"banking_loan_document_{i+1}.pdf")
