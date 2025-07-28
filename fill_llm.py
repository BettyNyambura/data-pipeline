import requests
import json
from pdfrw import PdfReader, PdfWriter, PdfDict
import os

# === Step 1: Extract fields from PDF ===
def extract_field_names(pdf_path):
    pdf = PdfReader(pdf_path)
    fields = set()
    for page in pdf.pages:
        if page.Annots:
            for annot in page.Annots:
                if annot.T:
                    fields.add(annot.T.to_unicode())
    return list(fields)

# === Step 2: Ask model to fill them ===
def get_filled_data_from_model(field_names):
    url = "http://34.67.118.142:8001/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    prompt = (
        "You are filling an insurance proposal form. "
        "For each field name listed, provide a realistic dummy value (not blank). "
        "Respond in JSON format.\n\nFields:\n" + json.dumps(field_names)
    )

    payload = {
        "model": "Qwen/Qwen3-32B-AWQ",  # replace with your actual model name
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print("❌ Model response not valid JSON:\n", content)
        raise

    return data

# === Step 3: Fill PDF ===
def fill_pdf(input_pdf_path, output_pdf_path, field_data):
    pdf = PdfReader(input_pdf_path)
    for page in pdf.pages:
        if page.Annots:
            for annot in page.Annots:
                if annot.T:
                    field_name = annot.T.to_unicode()
                    value = field_data.get(field_name, "")
                    annot.V = PdfDict(V=str(value))
                    annot.AP = None  # Refresh appearance
    PdfWriter(output_pdf_path, trailer=pdf).write()

# === MAIN ===
input_pdf = "proposal2.pdf"
output_dir = "filled_pdfs_ai"
os.makedirs(output_dir, exist_ok=True)

field_names = extract_field_names(input_pdf)

for i in range(1):
    print(f"\n📨 Requesting model to fill form #{i+1}...")
    filled_data = get_filled_data_from_model(field_names)

    output_path = os.path.join(output_dir, f"ai_filled_form_{i+1}.pdf")
    fill_pdf(input_pdf, output_path, filled_data)
    print(f"✅ Saved {output_path}")