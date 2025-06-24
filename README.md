# Filesure ADT-1 Automated Data Extractor

This project extracts structured data and generates a plain-English AI-style summary from MCA Form ADT-1 (PDF) filings using Python and PyMuPDF.

## Features

- Automatically extracts:
  - Company name, CIN, registered office, and email
  - Auditor’s name, PAN, FRN/membership, email, and address
  - Appointment dates, period, and nature of appointment
- Outputs structured data in `output.json`
- Generates an AI-style summary in `summary.txt` (in the style requested by Filesure)
- Uses pattern-based, robust heuristics for field extraction (not hardcoded line numbers)

## Requirements

- Python 3.7 or above
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) (`pip install pymupdf`)

## How to Use

1. **Clone or download this repository.**
2. **Place your `Form ADT-1-29092023_signed.pdf` file** in the project folder.
3. **Install required Python packages:**
    ```bash
    pip install pymupdf
    ```
4. **Run the extractor script:**
    ```bash
    python extractor.py
    ```
5. **Check the results:**
    - `output.json` — contains all structured extracted fields
    - `summary.txt` — contains a concise, human-readable summary

## Notes

- The script is designed to work with MCA’s standard ADT-1 PDF format and may require minor adjustments if the field order or format changes in future filings.
- For best results, ensure your PDF is text-based (not a scanned image-only file).
