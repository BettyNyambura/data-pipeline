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

def generate_insurance_application(filename):
    styles = getSampleStyleSheet()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        elements = []

        elements.append(Paragraph("INSURANCE APPLICATION FORM", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Section 1: Personal Information
        elements.append(Paragraph("1. Personal Information", styles["Heading2"]))
        personal_info = [
            ["Full Name", fake.name()],
            ["Date of Birth", fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d")],
            ["Gender", fake.random_element(["Male", "Female"])],
            ["Marital Status", fake.random_element(["Single", "Married", "Divorced", "Widowed"])],
            ["Phone Number", fake.phone_number()],
            ["Email", fake.email()],
            ["ID/Passport Number", fake.ssn()],
            ["Nationality", fake.country()],
            ["Residential Address", fake.address().replace("\n", ", ")],
        ]
        elements.append(Table(personal_info, colWidths=[150, 300], style=[
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(Spacer(1, 12))

        # Section 2: Employment Information
        elements.append(Paragraph("2. Employment Information", styles["Heading2"]))
        job_info = [
            ["Occupation", fake.job()],
            ["Employer Name", fake.company()],
            ["Work Phone", fake.phone_number()],
            ["Employment Type", fake.random_element(["Permanent", "Contract", "Self-Employed"])],
            ["Monthly Income (KES)", f"{random.randint(30000, 300000):,}"],
        ]
        elements.append(Table(job_info, colWidths=[150, 300], style=[
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ]))
        elements.append(Spacer(1, 12))

        # Section 3: Policy Details
        elements.append(Paragraph("3. Insurance Coverage Details", styles["Heading2"]))
        policy_info = [
            ["Type of Cover", fake.random_element(["Life", "Medical", "Vehicle", "Education", "Travel"])],
            ["Sum Assured (KES)", f"{random.randint(500000, 5000000):,}"],
            ["Payment Frequency", fake.random_element(["Monthly", "Quarterly", "Annually"])],
            ["Preferred Start Date", fake.date_this_year().strftime("%Y-%m-%d")],
            ["Term (Years)", random.randint(5, 30)],
        ]
        elements.append(Table(policy_info, colWidths=[180, 270], style=[
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ]))
        elements.append(Spacer(1, 12))

        # Section 4: Medical Disclosure
        elements.append(Paragraph("4. Medical Disclosure", styles["Heading2"]))
        medical = fake.paragraph(nb_sentences=3)
        elements.append(Paragraph(f"Have you been diagnosed with any illness in the last 5 years? {fake.random_element(['Yes', 'No'])}", styles["Normal"]))
        elements.append(Paragraph(f"If yes, provide details: {medical}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Section 5: Beneficiaries
        elements.append(Paragraph("5. Beneficiaries", styles["Heading2"]))
        beneficiaries = [["Name", "Relationship", "DOB", "Share %", "Contact"]]
        for _ in range(random.randint(1, 3)):
            beneficiaries.append([
                fake.name(),
                fake.random_element(["Spouse", "Child", "Sibling", "Parent"]),
                fake.date_of_birth(minimum_age=0, maximum_age=60).strftime("%Y-%m-%d"),
                f"{random.choice([50, 30, 20])}%",
                fake.phone_number()
            ])
        elements.append(Table(beneficiaries, colWidths=[120, 90, 80, 60, 100], style=[
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))
        elements.append(Spacer(1, 12))

        # Section 6: Declaration
        elements.append(Paragraph("6. Declaration & Signature", styles["Heading2"]))
        declaration = (
            "I hereby declare that all the information provided above is true and complete to the best of my knowledge. "
            "I understand that any misrepresentation may lead to the denial of insurance coverage or claims."
        )
        elements.append(Paragraph(declaration, styles["Normal"]))
        elements.append(Spacer(1, 18))
        elements.append(Paragraph(f"Signature: ________________________     Date: {fake.date_this_month()}", styles["Normal"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"Agent Name: {fake.name()}     Code: {random.randint(100000,999999)}", styles["Normal"]))

        doc.build(elements)
        upload_to_gcs(
            BUCKET_NAME,
            tmp.name,
            f"Insurance/Policy and Underwriting/Insurance Application/{filename}"
        )

# === MAIN ===
if __name__ == "__main__":
    for i in range(150):
        print(f"📄 Generating insurance_application_{i+1}.pdf ...")
        generate_insurance_application(f"insurance_application_{i+1}.pdf")
