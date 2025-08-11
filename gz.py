from google.cloud import storage
import os
import gzip
import shutil
import tempfile
import json
import markdown
from bs4 import BeautifulSoup

# Initialize GCP client
client = storage.Client()
bucket_name = "dummy-dromos-documents"
bucket = client.bucket(bucket_name)

source_prefix = "Healthcare/pdf/"
destination_prefix = "Healthcare/txt/"

# Supported extensions
SUPPORTED_TYPES = ['.gz', '.json', '.md', '.html', '.csv']

def extract_text_from_file(temp_file_path, content_type):
    if content_type.endswith('.gz'):
        with gzip.open(temp_file_path, 'rt', encoding='utf-8') as f:
            return f.read()
    elif content_type.endswith('.json'):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2)
    elif content_type.endswith('.md'):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif content_type.endswith('.html'):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text()
    elif content_type.endswith('.csv'):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return None

def process_files():
    blobs = list(bucket.list_blobs(prefix=source_prefix))

    for blob in blobs:
        filename = os.path.basename(blob.name)
        if not filename or blob.name.endswith('/'):
            continue

        if not any(filename.endswith(ext) for ext in SUPPORTED_TYPES):
            print(f"Skipping unsupported file: {filename}")
            continue

        print(f"Processing: {filename}")
        _, ext = os.path.splitext(filename)

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                blob.download_to_filename(temp_file.name)
                temp_file_path = temp_file.name

            text_data = extract_text_from_file(temp_file_path, ext)
            if text_data is None:
                print(f"Unsupported or empty content in: {filename}")
                continue

            # Upload to txt folder
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            new_blob_path = os.path.join(destination_prefix, txt_filename)
            new_blob = bucket.blob(new_blob_path)
            new_blob.upload_from_string(text_data, content_type='text/plain')
            print(f"✅ Uploaded: {new_blob_path}")

            # Delete original file from bucket
            blob.delete()
            print(f"🗑️ Deleted original: {blob.name}")

        except Exception as e:
            print(f"❌ Failed to process {filename}: {e}")

        finally:
            try:
                os.remove(temp_file_path)
            except Exception as cleanup_err:
                print(f"Could not delete temp file: {cleanup_err}")

if __name__ == "__main__":
    process_files()
