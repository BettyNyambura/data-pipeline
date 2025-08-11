from google.cloud import storage

def list_pdf_file_types(bucket_name="dummy-dromos-documents", folder_prefix="Healthcare/pdf/"):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=folder_prefix)
    file_types = {}

    for blob in blobs:
        if blob.name.endswith("/"):
            continue  # skip "folder" entries

        extension = blob.name.split('.')[-1].lower()
        file_types[extension] = file_types.get(extension, 0) + 1

    print("File types in Healthcare/pdf/:")
    for ext, count in file_types.items():
        print(f".{ext}: {count} file(s)")

# Run the function
list_pdf_file_types()