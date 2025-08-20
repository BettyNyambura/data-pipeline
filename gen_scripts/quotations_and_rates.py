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
BASE_PATH = "Insurance/Policy and Underwriting/Quotation Sheets & Rate Quotes"

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_path)
    print(f"✅ Uploaded: gs://{bucket_name}/{destination_blob_name}")

def generate_quotation_sheet(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Insurance Quotation Sheet", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Date Issued: {fake.date_this_year()}", styles["Normal"]))
        elements.append(Paragraph(f"Prepared By: {fake.name()} – {fake.company()}", styles["Normal"]))
        elements.append(Paragraph(f"Client Name: {fake.name()}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        data = [["Coverage Type", "Sum Assured", "Term (Years)", "Annual Premium", "Payment Frequency"]]
        for _ in range(random.randint(2, 5)):
            data.append([
                fake.random_element(["Life", "Medical", "Vehicle", "Property"]),
                f"KES {random.randint(100000, 5000000):,}",
                random.randint(5, 20),
                f"KES {random.randint(5000, 100000):,}",
                fake.random_element(["Monthly", "Quarterly", "Annually"]),
            ])

        table = Table(data, colWidths=[100, 100, 80, 100, 100])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("This quotation is subject to underwriting and further assessment.", styles["Italic"]))
        doc.build(elements)

        upload_to_gcs(BUCKET_NAME, tmp.name, f"{BASE_PATH}/{filename}")

def generate_rate_quote(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("Rate Quote Summary", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Product Name: {fake.random_element(['SecurePlan', 'LifeCover', 'FlexCare'])}", styles["Normal"]))
        elements.append(Paragraph(f"Prepared By: {fake.name()}", styles["Normal"]))
        elements.append(Paragraph(f"Date: {fake.date_this_year()}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        rate_data = [["Age Band", "Male Rate / 1000", "Female Rate / 1000", "Sum Assured", "Comments"]]
        for age in range(18, 66, 4):
            male_rate = round(random.uniform(2.5, 7.5), 2)
            female_rate = round(male_rate - random.uniform(0.2, 0.8), 2)
            sum_assured = f"KES {random.choice([250000, 500000, 1000000]):,}"
            comments = fake.random_element(["Standard", "Smoker Loading", "Preferred Rate"])
            rate_data.append([f"{age}-{age+3}", male_rate, female_rate, sum_assured, comments])

        table = Table(rate_data, colWidths=[70, 90, 90, 100, 100])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Note: All rates are indicative and subject to underwriting.", styles["Italic"]))

        doc.build(elements)
        upload_to_gcs(BUCKET_NAME, tmp.name, f"{BASE_PATH}/{filename}")

# === MAIN ===
if __name__ == "__main__":
    for i in range(150):
        generate_quotation_sheet(f"quotation_sheet_{i+1}.pdf")

    for i in range(150):
        generate_rate_quote(f"rate_quote_{i+1}.pdf")
