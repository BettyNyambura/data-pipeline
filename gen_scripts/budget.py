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
SUBTYPES = ["Operating Budget", "Financial Forecast", "Business Plan Financials"]

# === Upload Function ===
def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

# === Document Generators ===
def generate_operating_budget(style):
    rows = [["Department", "Budgeted Amount", "Actual Spend", "Variance"]]
    for _ in range(6):
        budget = random.randint(10000, 100000)
        actual = random.randint(int(budget * 0.8), int(budget * 1.2))
        variance = actual - budget
        rows.append([
            fake.bs().title(),
            f"${budget:,.2f}",
            f"${actual:,.2f}",
            f"${variance:,.2f}"
        ])
    return [
        Paragraph("Operating Budget Overview", style["Title"]),
        Spacer(1, 12),
        Paragraph(f"Fiscal Year: {datetime.now().year}", style["Normal"]),
        Spacer(1, 12),
        Table(rows, colWidths=[180, 110, 110, 110], style=TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ])),
        Spacer(1, 12),
        Paragraph("Comments:", style["Heading2"]),
        Paragraph(fake.paragraph(nb_sentences=3), style["Normal"])
    ]

def generate_financial_forecast(style):
    rows = [["Month", "Revenue", "Expenses", "Net Profit"]]
    for month in range(1, 13):
        revenue = random.randint(50000, 150000)
        expenses = random.randint(30000, 130000)
        net = revenue - expenses
        rows.append([
            datetime(2025, month, 1).strftime('%B'),
            f"${revenue:,.2f}",
            f"${expenses:,.2f}",
            f"${net:,.2f}"
        ])
    return [
        Paragraph("Financial Forecast - 12 Month Projection", style["Title"]),
        Spacer(1, 12),
        Table(rows, colWidths=[120, 120, 120, 120], style=TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.beige),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ])),
        Spacer(1, 12),
        Paragraph("Forecast Based on Historical Trends and Current Assumptions.", style["Normal"])
    ]

def generate_business_plan_financials(style):
    data = [
        ["Initial Capital", f"${random.randint(100000, 500000):,.2f}"],
        ["Projected Year 1 Revenue", f"${random.randint(200000, 800000):,.2f}"],
        ["Projected Year 1 Net Profit", f"${random.randint(50000, 300000):,.2f}"],
        ["Break-even Point", f"{random.randint(6, 18)} months"],
        ["Cash Flow Reserve", f"${random.randint(20000, 100000):,.2f}"],
    ]
    return [
        Paragraph("Business Plan - Key Financial Figures", style["Title"]),
        Spacer(1, 12),
        Table(data, colWidths=[250, 250], style=TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ])),
        Spacer(1, 12),
        Paragraph("Prepared by: " + fake.name(), style["Normal"]),
        Paragraph("Date: " + datetime.now().strftime("%Y-%m-%d"), style["Normal"]),
        Spacer(1, 12),
        Paragraph("Notes:", style["Heading2"]),
        Paragraph(fake.paragraph(nb_sentences=4), style["Normal"])
    ]

# === Main Document Builder ===
def generate_budget_document_file(filename):
    styles = getSampleStyleSheet()
    subtype = random.choice(SUBTYPES)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        elements = []

        # Metadata Table
        meta = [
            ["Document Type", subtype],
            ["Prepared For", fake.company()],
            ["Prepared By", fake.name()],
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
        if subtype == "Operating Budget":
            elements += generate_operating_budget(styles)
        elif subtype == "Financial Forecast":
            elements += generate_financial_forecast(styles)
        elif subtype == "Business Plan Financials":
            elements += generate_business_plan_financials(styles)

        doc.build(elements)

        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"{CATEGORY}/Budget_Planning_Documents/{subtype.replace(' ', '_')}/{filename}"
        )

# === Run Batch Generation ===
if __name__ == "__main__":
    for i in range(300):
        generate_budget_document_file(f"budget_doc_{i+1}.pdf")
