"""
OCR Engine Package.
"""
from app.engines.ocr.base import OCRStatus, OCRResult, OCRProvider
from app.engines.ocr.tesseract_provider import TesseractOCRProvider

__all__ = ["OCRStatus", "OCRResult", "OCRProvider", "TesseractOCRProvider"]
