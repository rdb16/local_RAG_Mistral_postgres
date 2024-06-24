import hashlib
from PyPDF2 import PdfReader
import os

from utils import parse_pdf_date


def get_pdf_details(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        return "File does not exist", None

    # Load the PDF file
    try:
        reader = PdfReader(file_path)
        # Get creation date from the document metadata
        creation_date = reader.metadata.get('/CreationDate', 'Unknown date')
    except Exception as e:
        return f"Error reading PDF metadata: {str(e)}", None

    # Calculate SHA-1 hash of the file
    sha1_hash = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                sha1_hash.update(chunk)
        sha1_hexdigest: str = sha1_hash.hexdigest()
    except Exception as e:
        return creation_date, f"Error calculating SHA1: {str(e)}"

    print("creation_date", creation_date)
    format_date = parse_pdf_date.parse(creation_date)

    return format_date, sha1_hexdigest
