from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from google.cloud import storage
from faker import Faker
import tempfile
import random

fake = Faker()
BUCKET_NAME = "dummy-dromos-documents"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_rating_worksheet(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Insurance Rating Worksheet", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Metadata
        elements.append(Paragraph(f"Product: {fake.random_element(['Life Shield', 'Secure Plan', 'Platinum Health'])}", styles["Normal"]))
        elements.append(Paragraph(f"Prepared By: {fake.name()}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Table Header
        data = [["Age", "Gender", "Sum Assured (KES)", "Rate per 1000", "Annual Premium (KES)"]]
        for age in range(18, 66, 2):
            gender = random.choice(["Male", "Female"])
            sum_assured = random.choice([250_000, 500_000, 1_000_000])
            rate = round(random.uniform(2.5, 8.5), 2)
            annual_premium = round(sum_assured * (rate / 1000), 2)
            data.append([age, gender, f"{sum_assured:,}", rate, f"{annual_premium:,}"])

        table = Table(data, colWidths=[50, 60, 130, 100, 130])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table)

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"Insurance/Policy and Underwriting/Rating Worksheets & Actuarial Tables/{filename}")

def generate_actuarial_table(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Actuarial Life Table", styles["Title"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Prepared By: {fake.name()}, FSA", styles["Normal"]))
        elements.append(Paragraph("Product Category: Long-Term Life Insurance", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Table Header
        data = [["Age (x)", "qx (Prob. of Death)", "lx (Lives Surviving)", "dx (Deaths)", "Tx (Total Future Years)", "ex (Life Expectancy)"]]
        lx = 100000
        Tx = 0
        for age in range(20, 91, 5):
            qx = round(random.uniform(0.001, 0.08), 4)
            dx = int(lx * qx)
            Tx += lx
            ex = round(Tx / lx, 2) if lx > 0 else 0
            data.append([age, qx, lx, dx, Tx, ex])
            lx -= dx
            if lx <= 0:
                break

        table = Table(data, colWidths=[50, 90, 100, 80, 100, 80])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table)

        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"Insurance/Policy and Underwriting/Rating Worksheets & Actuarial Tables/{filename}")

if __name__ == "__main__":
    for i in range(150):
        generate_rating_worksheet(f"rating_worksheet_{i+1}.pdf")
        print(f"📄 Creating: rating_worksheet_{i+1}.pdf")
    
    for i in range(150):
        generate_actuarial_table(f"actuarial_table_{i+1}.pdf")
        print(f"📄 Creating: ractuarial_table_{i+1}.pdf")