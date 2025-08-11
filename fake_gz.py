from google.cloud import storage
import gzip
import tempfile
import shutil
import os

bucket_name = "dummy-dromos-documents"
pdf_prefix = "Healthcare/pdf/"
txt_prefix = "Healthcare/txt/"

client = storage.Client()
bucket = client.bucket(bucket_name)

def is_gzipped(blob_data: bytes) -> bool:
    return blob_data[:2] == b'\x1f\x8b'

def process_blob(blob):
    filename = blob.name.split("/")[-1]
    print(f"🔍 Checking: {filename}")

    data = blob.download_as_bytes()

    if is_gzipped(data):
        print("📦 Compressed file. Decompressing...")
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as gz_file:
            gz_file.write(data)
            gz_path = gz_file.name

        try:
            with gzip.open(gz_path, 'rb') as f_in, tempfile.NamedTemporaryFile(delete=False, mode='wb') as out_file:
                shutil.copyfileobj(f_in, out_file)
                out_path = out_file.name

            new_filename = filename.replace('.gz', '.txt')
            txt_blob_path = txt_prefix + new_filename

            bucket.blob(txt_blob_path).upload_from_filename(out_path)
            print(f"✅ Decompressed and uploaded: {txt_blob_path}")
            blob.delete()
            print(f"🗑️ Deleted from PDF folder: {blob.name}")
        finally:
            os.remove(gz_path)
            os.remove(out_path)
    else:
        print("🟡 Not compressed. Renaming to .txt")
        new_filename = filename.replace('.gz', '.txt')
        txt_blob_path = txt_prefix + new_filename

        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tmp_file:
            tmp_file.write(data)
            tmp_path = tmp_file.name

        try:
            bucket.blob(txt_blob_path).upload_from_filename(tmp_path)
            print(f"✅ Uploaded as: {txt_blob_path}")
            blob.delete()
            print(f"🗑️ Deleted from PDF folder: {blob.name}")
        finally:
            os.remove(tmp_path)

def main():
    blobs = bucket.list_blobs(prefix=pdf_prefix)
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        process_blob(blob)

if __name__ == "__main__":
    main()
