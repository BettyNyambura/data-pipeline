#!/usr/bin/env python3
"""
GCS Document Organizer
Sorts documents in GCS bucket healthcare folder into pdf and txt subfolders
while keeping original files intact.
"""

import os
import io
import tempfile
from pathlib import Path
from google.cloud import storage
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class GCSDocumentOrganizer:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.healthcare_folder = "Healthcare/"
        self.pdf_folder = f"{self.healthcare_folder}pdf/"
        self.txt_folder = f"{self.healthcare_folder}txt/"

    def list_healthcare_files(self):
        blobs = self.bucket.list_blobs(prefix=self.healthcare_folder)
        return [blob for blob in blobs if not blob.name.endswith('/')]

    def get_file_extension(self, filename):
        return Path(filename).suffix.lower()

    def generate_sorted_filename(self, original_path, target_folder):
        filename = Path(original_path).name
        relative_path = original_path.replace(self.healthcare_folder, "", 1)
        path_parts = Path(relative_path).parts
        if len(path_parts) > 1:
            folder_prefix = "_".join(path_parts[:-1])
            original_filename = path_parts[-1]
            name_without_ext = Path(original_filename).stem
            extension = Path(original_filename).suffix
            filename = f"{folder_prefix}_{name_without_ext}{extension}"
        return f"{target_folder}{filename}"

    def csv_to_txt(self, csv_content, output_path):
        """
        Convert CSV content to plain TXT and upload to GCS
        """
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            text_data = df.to_string(index=False)
            blob = self.bucket.blob(output_path)
            blob.upload_from_string(text_data, content_type='text/plain')
            print(f"✓ Converted CSV to TXT: {output_path}")
        except Exception as e:
            print(f"✗ Error converting CSV to TXT {output_path}: {str(e)}")

    def copy_file_to_target(self, source_blob, target_path):
        try:
            self.bucket.copy_blob(source_blob, self.bucket, target_path)
            print(f"✓ Copied: {source_blob.name} -> {target_path}")
            return True
        except Exception as e:
            print(f"✗ Error copying {source_blob.name}: {str(e)}")
            return False

    def ensure_folders_exist(self):
        pdf_folder_blob = self.bucket.blob(f"{self.pdf_folder}")
        txt_folder_blob = self.bucket.blob(f"{self.txt_folder}")
        print(f"Target folders will be created: {self.pdf_folder} and {self.txt_folder}")
        print("All files will be flattened (no subfolders in output)")

    def organize_documents(self):
        print(f"Starting document organization in bucket: {self.bucket_name}")
        print(f"Healthcare folder: {self.healthcare_folder}")

        self.ensure_folders_exist()
        files = self.list_healthcare_files()
        print(f"Found {len(files)} files to process")

        stats = {
            'pdf_copied': 0,
            'txt_copied': 0,
            'csv_converted': 0,
            'other_converted': 0,
            'errors': 0
        }

        for blob in files:
            file_ext = self.get_file_extension(blob.name)
            print(f"\nProcessing: {blob.name} (Extension: {file_ext})")

            try:
                if file_ext == '.pdf':
                    target_path = self.generate_sorted_filename(blob.name, self.pdf_folder)
                    if self.copy_file_to_target(blob, target_path):
                        stats['pdf_copied'] += 1
                    else:
                        stats['errors'] += 1

                elif file_ext == '.txt':
                    target_path = self.generate_sorted_filename(blob.name, self.txt_folder)
                    if self.copy_file_to_target(blob, target_path):
                        stats['txt_copied'] += 1
                    else:
                        stats['errors'] += 1

                elif file_ext == '.csv':
                    # ✅ CSV converted to TXT instead of PDF
                    csv_content = blob.download_as_text()
                    original_name = blob.name
                    txt_name = original_name.rsplit('.', 1)[0] + '.txt'
                    target_path = self.generate_sorted_filename(txt_name, self.txt_folder)
                    self.csv_to_txt(csv_content, target_path)
                    stats['csv_converted'] += 1

                else:
                    # For other files, copy to PDF folder as-is
                    target_path = self.generate_sorted_filename(blob.name, self.pdf_folder)
                    if self.copy_file_to_target(blob, target_path):
                        stats['other_converted'] += 1
                        print(f"  Note: {file_ext} file moved to PDF folder without conversion")
                    else:
                        stats['errors'] += 1

            except Exception as e:
                print(f"✗ Unexpected error processing {blob.name}: {str(e)}")
                stats['errors'] += 1

        print("\n" + "="*50)
        print("ORGANIZATION COMPLETE!")
        print("="*50)
        print(f"PDF files copied: {stats['pdf_copied']}")
        print(f"TXT files copied: {stats['txt_copied']}")
        print(f"CSV files converted to TXT: {stats['csv_converted']}")
        print(f"Other files moved: {stats['other_converted']}")
        print(f"Errors encountered: {stats['errors']}")
        print(f"Total files processed: {sum(stats.values())}")
        print("\nOriginal files remain intact in their original locations.")
        print("All output files are flattened in pdf/ and txt/ folders (no subfolders).")

def main():
    BUCKET_NAME = "dummy-dromos-documents"
    organizer = GCSDocumentOrganizer(BUCKET_NAME)
    organizer.organize_documents()

if __name__ == "__main__":
    main()
