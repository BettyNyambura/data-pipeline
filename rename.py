import os
import gzip
from io import BytesIO
from google.cloud import storage
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

BUCKET_NAME = "dummy-dromos-documents"
PDF_FOLDER = "Healthcare/pdf/"

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

def is_valid_gzip(content: bytes) -> bool:
    """Check if the content is actually gzipped."""
    try:
        with gzip.GzipFile(fileobj=BytesIO(content)) as f:
            f.read(1)
        return True
    except:
        return False

def rename_invalid_gz(blob):
    """Rename the blob if it's not a real .gz file."""
    logger.info(f"📄 Checking: {blob.name}")
    content = blob.download_as_bytes()

    if is_valid_gzip(content):
        logger.info("✅ Valid gzip. Skipping.")
        return

    # It's not actually gzipped
    new_name = blob.name[:-3]  # Remove .gz extension
    logger.info(f"⚠️ Not a valid gzip. Renaming to: {new_name}")

    # Upload content to new blob name (same content)
    new_blob = bucket.blob(new_name)
    new_blob.upload_from_string(content)

    # Delete old .gz blob
    blob.delete()
    logger.info(f"✅ Renamed and replaced: {blob.name} ➜ {new_name}")

def main():
    logger.info("🚀 Starting to scan and rename invalid .gz files...")
    blobs = client.list_blobs(BUCKET_NAME, prefix=PDF_FOLDER)

    for blob in blobs:
        if blob.name.endswith(".gz"):
            rename_invalid_gz(blob)

if __name__ == "__main__":
    main()
