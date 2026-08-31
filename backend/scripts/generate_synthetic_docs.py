"""
Synthetic Document Generator Script.

Creates safe, non-PII synthetic document fixtures for testing and SIH demonstration:
1. clean_digital_tender.pdf
2. scanned_tender.pdf
3. poor_scanned_doc.pdf
4. bidder_credentials.pdf (Shakti Infrastructure Solutions Pvt Ltd)
5. financial_statement.pdf (Turnover: ₹15.0 Crore)
6. experience_certificate.pdf
7. conflicting_identifiers.pdf
8. incomplete_document.pdf
9. corrupted_document.pdf
"""
import os
import fitz  # PyMuPDF

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")

def create_synthetic_pdf(filepath: str, text_content: str, is_scanned: bool = False):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    if not is_scanned:
        # Insert text directly
        page.insert_text((50, 50), text_content, fontsize=11)
    else:
        # Render text onto pixmap to simulate scanned document with low/no native text
        pix_doc = fitz.open()
        p = pix_doc.new_page(width=595, height=842)
        p.insert_text((50, 50), text_content, fontsize=10)
        pix = p.get_pixmap(dpi=100)
        
        # Insert image into target page
        page.insert_image(page.rect, stream=pix.tobytes("png"))
        pix_doc.close()

    doc.save(filepath)
    doc.close()
    print(f"✓ Generated: {filepath}")

def main():
    print("Generating synthetic document fixtures...")

    # 1. Clean Tender
    create_synthetic_pdf(
        os.path.join(FIXTURES_DIR, "clean_digital_tender.pdf"),
        "NOTICE INVITING TENDER\nGeM Bid Number: GEM/2026/B/8899123\nTitle: Procurement of Smart Infrastructure Hardware\nEstimated Value: INR 5,00,00,000 (5 Crore)\nSubmission Deadline: 2026-10-15\nEligibility: Minimum Annual Turnover of 10 Crore in last 3 financial years."
    )

    # 2. Scanned Tender
    create_synthetic_pdf(
        os.path.join(FIXTURES_DIR, "scanned_tender.pdf"),
        "SCANNED TENDER SPECIFICATION\nGeM Bid Ref: GEM/2026/B/990011\nRequired Qualification: PAN, GSTIN, and MCA Certificate.",
        is_scanned=True
    )

    # 3. Bidder Credentials Document
    create_synthetic_pdf(
        os.path.join(FIXTURES_DIR, "bidder_credentials.pdf"),
        "COMPANY PROFILE & REGISTRATION\nLegal Name: Shakti Infrastructure Solutions Pvt Ltd\nTrade Name: Shakti Infra\nPAN: AADCB2230M\nGSTIN: 27AADCB2230M1ZP\nCIN: U72900MH2020PTC345678\nUdyam: UDYAM-MH-01-0000001\nEmail: contact@shaktiinfra.local\nPhone: +919876543210\nAddress: Plot 42, MIDC Industrial Area, Mumbai, Maharashtra 400093"
    )

    # 4. Financial Statement
    create_synthetic_pdf(
        os.path.join(FIXTURES_DIR, "financial_statement.pdf"),
        "AUDITED FINANCIAL STATEMENT - FY 2024-2025\nCompany: Shakti Infrastructure Solutions Pvt Ltd\nAnnual Turnover: 15.0 Crore INR\nNet Worth: 4.5 Crore INR\nChartered Accountant: M/s Sharma & Associates\nUDIN: 24012345AAAAAB1234"
    )

    # 5. Experience Certificate
    create_synthetic_pdf(
        os.path.join(FIXTURES_DIR, "experience_certificate.pdf"),
        "COMPLETION CERTIFICATE\nClient: Maharashtra State Electricity Board\nProject: Smart Meter Installation\nContract Value: INR 12,50,00,000\nStatus: Satisfactory Completion on 2025-03-31\nCertificate No: MSEB/EXP/2025/441"
    )

    # 6. Conflicting Document
    create_synthetic_pdf(
        os.path.join(FIXTURES_DIR, "conflicting_identifiers.pdf"),
        "MISMATCHED DECLARATION\nCompany Name: Shakti Infra Solutions\nPAN: ZZZZZ9999Z\nGSTIN: 99XXXXX0000X0Z0"
    )

    # 7. Corrupted document
    corrupted_path = os.path.join(FIXTURES_DIR, "corrupted_document.pdf")
    with open(corrupted_path, "wb") as f:
        f.write(b"NOT_A_VALID_PDF_FILE_HEADER_BINARY_DATA_CORRUPTED")
    print(f"✓ Generated: {corrupted_path}")

    print("All synthetic fixtures generated successfully.")

if __name__ == "__main__":
    main()
