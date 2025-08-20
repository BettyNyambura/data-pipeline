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
SUBTYPES = ["Balance Sheet", "Income Statement", "Cash Flow Statement"]

# === Upload Function ===
def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

# === Generate Document ===
def generate_financial_statement_file(filename):
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle("wrap", fontSize=8, leading=10)
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
            ["Company", fake.company()],
            ["Report Type", subtype],
            ["Fiscal Year Ending", fake.date_this_decade().strftime("%Y-%m-%d")],
            ["Prepared By", fake.name()],
        ]
        meta_table = Table(meta, colWidths=[150, 330])
        meta_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 16))

        # === Statement Type Logic ===
        if subtype == "Balance Sheet":
            elements += generate_balance_sheet(normal)
        elif subtype == "Income Statement":
            elements += generate_income_statement(normal)
        elif subtype == "Cash Flow Statement":
            elements += generate_cashflow_statement(normal)

        # === Summary ===
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Summary Notes", styles["Heading2"]))
        elements.append(Paragraph(fake.paragraph(nb_sentences=4), normal))

        doc.build(elements)

        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{CATEGORY}/{subtype.replace(' ', '_')}/{filename}"
        )

# === Subtype Content Builders ===
def generate_balance_sheet(style):
    assets = [
        ["Cash and Equivalents", random_amount()],
        ["Accounts Receivable", random_amount()],
        ["Inventory", random_amount()],
        ["Prepaid Expenses", random_amount()],
        ["Total Current Assets", ""],
        ["Property, Plant, and Equipment", random_amount()],
        ["Intangible Assets", random_amount()],
        ["Total Non-Current Assets", ""],
        ["Total Assets", ""],
    ]

    liabilities = [
        ["Accounts Payable", random_amount()],
        ["Accrued Expenses", random_amount()],
        ["Short-term Loans", random_amount()],
        ["Total Current Liabilities", ""],
        ["Long-term Debt", random_amount()],
        ["Deferred Tax", random_amount()],
        ["Total Non-Current Liabilities", ""],
        ["Total Liabilities", ""],
    ]

    equity = [
        ["Common Stock", random_amount()],
        ["Retained Earnings", random_amount()],
        ["Total Equity", ""],
    ]

    return [
        Paragraph("Assets", style),
        financial_table(assets),
        Spacer(1, 12),
        Paragraph("Liabilities", style),
        financial_table(liabilities),
        Spacer(1, 12),
        Paragraph("Equity", style),
        financial_table(equity)
    ]

def generate_income_statement(style):
    income = [
        ["Revenue", random_amount()],
        ["Cost of Goods Sold", f"-{random_amount()}"],
        ["Gross Profit", ""],
        ["Operating Expenses", f"-{random_amount()}"],
        ["Operating Income", ""],
        ["Interest Expense", f"-{random_amount()}"],
        ["Income Before Taxes", ""],
        ["Tax Expense", f"-{random_amount()}"],
        ["Net Income", ""],
    ]
    return [
        Paragraph("Income Statement Breakdown", style),
        financial_table(income)
    ]

def generate_cashflow_statement(style):
    cashflow = [
        ["Net Income", random_amount()],
        ["Depreciation & Amortization", random_amount()],
        ["Changes in Working Capital", f"-{random_amount()}"],
        ["Net Cash from Operating Activities", ""],
        ["Capital Expenditures", f"-{random_amount()}"],
        ["Net Cash from Investing Activities", ""],
        ["Loan Proceeds", random_amount()],
        ["Loan Repayment", f"-{random_amount()}"],
        ["Net Cash from Financing Activities", ""],
        ["Net Change in Cash", ""],
    ]
    return [
        Paragraph("Cash Flow Breakdown", style),
        financial_table(cashflow)
    ]

# === Helpers ===
def random_amount():
    return f"${round(random.uniform(1000, 250000), 2):,.2f}"

def financial_table(data):
    t = Table(data, colWidths=[300, 150])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (1,1), (-1,-1), colors.black),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ]))
    return t

# === Main Runner ===
if __name__ == "__main__":
    for i in range(300):
        generate_financial_statement_file(f"financial_statement_{i+1}.pdf")
