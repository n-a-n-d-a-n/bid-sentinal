"""
PDF Document Parser using PyMuPDF (fitz).

Features:
- Safe PDF opening & metadata inspection
- Native text extraction per page
- OCR requirement detection (scanned vs native PDF)
- High-quality page rendering (for OCR or page previews)
- Text statistics & layout metrics preservation
"""
import fitz  # PyMuPDF
import structlog
from typing import List, Dict, Any, Optional, Tuple

logger = structlog.get_logger(__name__)

class ParsedPage:
    def __init__(
        self,
        page_number: int,
        raw_text: str,
        word_count: int,
        char_count: int,
        is_scanned: bool,
        ocr_required: bool,
        image_count: int,
        width: int,
        height: int,
        rendered_image: Optional[bytes] = None,
    ):
        self.page_number = page_number
        self.raw_text = raw_text
        self.word_count = word_count
        self.char_count = char_count
        self.is_scanned = is_scanned
        self.ocr_required = ocr_required
        self.image_count = image_count
        self.width = width
        self.height = height
        self.rendered_image = rendered_image

class DocumentParserService:
    @staticmethod
    def parse_pdf(pdf_bytes: bytes, render_pages: bool = False) -> Tuple[Dict[str, Any], List[ParsedPage]]:
        """
        Parses PDF bytes and extracts structured page information.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.error("pdf_open_failed", error=str(e))
            raise ValueError(f"Invalid or corrupted PDF file: {e}")

        doc_metadata = {
            "page_count": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "creator": doc.metadata.get("creator", ""),
            "format": doc.metadata.get("format", "PDF"),
            "encryption": doc.is_encrypted,
        }

        parsed_pages: List[ParsedPage] = []

        for page_idx in range(len(doc)):
            page_num = page_idx + 1
            page = doc[page_idx]

            rect = page.rect
            width = int(rect.width)
            height = int(rect.height)

            # Native text extraction
            text = page.get_text("text") or ""
            text_strip = text.strip()
            char_count = len(text_strip)
            word_count = len(text_strip.split())

            # Count images on the page
            image_list = page.get_images()
            image_count = len(image_list)

            # OCR requirement logic:
            # If native text has fewer than 40 characters and image_count > 0 or word_count < 10,
            # mark as scanned / OCR required.
            is_scanned = (char_count < 40) and (image_count > 0 or word_count < 10)
            ocr_required = is_scanned or (char_count < 30)

            rendered_bytes = None
            if render_pages or ocr_required:
                # Render page to PNG image (dpi=150)
                pix = page.get_pixmap(dpi=150)
                rendered_bytes = pix.tobytes("png")

            parsed_page = ParsedPage(
                page_number=page_num,
                raw_text=text,
                word_count=word_count,
                char_count=char_count,
                is_scanned=is_scanned,
                ocr_required=ocr_required,
                image_count=image_count,
                width=width,
                height=height,
                rendered_image=rendered_bytes,
            )
            parsed_pages.append(parsed_page)

        doc.close()
        return doc_metadata, parsed_pages

document_parser = DocumentParserService()
