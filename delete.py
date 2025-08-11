from google.cloud import storage

# Initialize client and bucket
bucket_name = "dummy-dromos-documents"
folder_prefix = "Healthcare/pdf/"
client = storage.Client()
bucket = client.bucket(bucket_name)

# List of files that failed to process (filenames only, not full paths)
failed_files = {
    "mimic-iv-note-deidentified-free-text-clinical-notes-2.2_note_radiology.csv.gz",
    "physionet.org_files_mimiciii_1.4_DATETIMEEVENTS.csv.gz",
    "physionet.org_files_mimiciii_1.4_DIAGNOSES_ICD.csv.gz",
    "physionet.org_files_mimiciii_1.4_DRGCODES.csv.gz",
    "physionet.org_files_mimiciii_1.4_D_ICD_DIAGNOSES.csv.gz",
    "physionet.org_files_mimiciii_1.4_INPUTEVENTS_MV.csv.gz",
    "physionet.org_files_mimiciii_1.4_LABEVENTS.csv.gz",
    "physionet.org_files_mimiciii_1.4_OUTPUTEVENTS.csv.gz",
    "physionet.org_files_mimiciii_1.4_PRESCRIPTIONS.csv.gz",
    "physionet.org_files_mimiciii_1.4_PROCEDUREEVENTS_MV.csv.gz",
    "physionet.org_files_mimiciii_1.4_PROCEDURES_ICD.csv.gz",
    "physionet.org_files_mimiciii_1.4_SERVICES.csv.gz",
    "physionet.org_files_mimiciii_1.4_TRANSFERS.csv.gz"
}

def clean_pdf_folder():
    blobs = bucket.list_blobs(prefix=folder_prefix)

    for blob in blobs:
        filename = blob.name.split("/")[-1]
        if not filename or filename.endswith("/"):
            continue

        if filename not in failed_files:
            print(f"Deleting: {blob.name}")
            blob.delete()

    print("✅ Cleanup complete. Only failed files remain.")

if __name__ == "__main__":
    clean_pdf_folder()
