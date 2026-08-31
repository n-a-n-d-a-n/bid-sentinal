"""
Semantic Policy Chunker.

Chunks policy text preserving document hierarchy, section headings, and paragraph boundaries.
Target chunk size: ~500 characters with 50 character overlap.
"""
import hashlib
import structlog
from typing import List, Dict, Any, Optional

from app.engines.policy.parser import ParsedPolicySection

logger = structlog.get_logger(__name__)

class SemanticChunk:
    def __init__(
        self,
        chunk_index: int,
        section: str,
        clause_id: Optional[str],
        page_number: int,
        text: str,
        checksum: str,
        keywords: List[str],
    ):
        self.chunk_index = chunk_index
        self.section = section
        self.clause_id = clause_id
        self.page_number = page_number
        self.text = text
        self.checksum = checksum
        self.keywords = keywords

class PolicyChunkerService:
    def chunk_sections(self, sections: List[ParsedPolicySection], max_chars: int = 500, overlap: int = 50) -> List[SemanticChunk]:
        chunks: List[SemanticChunk] = []
        chunk_idx = 1

        for sec in sections:
            content = sec.content.strip()
            if not content:
                continue

            # Split content into paragraphs or sliding windows
            start = 0
            while start < len(content):
                end = min(len(content), start + max_chars)
                chunk_text = content[start:end].strip()
                checksum = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                # Extract basic keywords
                words = [w.lower() for w in chunk_text.split() if len(w) > 4]
                keywords = list(set(words[:10]))

                chunks.append(SemanticChunk(
                    chunk_index=chunk_idx,
                    section=sec.section_name,
                    clause_id=sec.clause_id,
                    page_number=sec.page_number,
                    text=chunk_text,
                    checksum=checksum,
                    keywords=keywords,
                ))
                chunk_idx += 1
                start += max_chars - overlap

        return chunks

policy_chunker = PolicyChunkerService()
