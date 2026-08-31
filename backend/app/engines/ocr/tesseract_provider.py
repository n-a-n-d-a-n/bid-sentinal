"""
Tesseract OCR Provider.

Provides image-to-text extraction using pytesseract.
Safely handles environments where Tesseract binary or pytesseract library is missing.
"""
import io
import structlog
from typing import Optional

from app.engines.ocr.base import OCRProvider, OCRResult, OCRStatus

logger = structlog.get_logger(__name__)

class TesseractOCRProvider(OCRProvider):
    engine_name: str = "TESSERACT"

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd

    async def extract_text(self, image_bytes: bytes, page_number: int) -> OCRResult:
        if not image_bytes:
            return OCRResult(
                status=OCRStatus.FAILED,
                extracted_text="",
                confidence=0.0,
                engine_name=self.engine_name,
                page_number=page_number,
                error_message="Empty image bytes provided for OCR.",
            )

        try:
            from PIL import Image
            import pytesseract

            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

            image = Image.open(io.BytesIO(image_bytes))

            # Perform OCR
            ocr_text = pytesseract.image_to_string(image)
            
            # Get OCR confidence metadata if available
            confidence = 0.85
            try:
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                confs = [float(c) for c in data.get("conf", []) if c != "-1" and str(c).replace(".","").isdigit()]
                if confs:
                    confidence = round(sum(confs) / len(confs) / 100.0, 2)
            except Exception:
                pass

            return OCRResult(
                status=OCRStatus.COMPLETED,
                extracted_text=ocr_text.strip(),
                confidence=confidence,
                engine_name=self.engine_name,
                page_number=page_number,
            )
        except ImportError as ie:
            logger.warning("tesseract_import_missing", error=str(ie))
            return OCRResult(
                status=OCRStatus.UNAVAILABLE,
                extracted_text="",
                confidence=0.0,
                engine_name=self.engine_name,
                page_number=page_number,
                error_message="pytesseract or PIL library not installed in environment.",
            )
        except Exception as exc:
            logger.warning("tesseract_ocr_execution_failed", error=str(exc))
            return OCRResult(
                status=OCRStatus.UNAVAILABLE,
                extracted_text="",
                confidence=0.0,
                engine_name=self.engine_name,
                page_number=page_number,
                error_message=f"Tesseract OCR binary not found or execution failed: {str(exc)}",
            )
