"""
Policy Document Parser.

Parses policy text/PDFs, identifying section headings, clause IDs, and page numbers.
"""
import re
import structlog
from typing import List, Dict, Any, Optional

logger = structlog.get_logger(__name__)

class ParsedPolicySection:
    def __init__(self, section_name: str, clause_id: Optional[str], page_number: int, content: str):
        self.section_name = section_name
        self.clause_id = clause_id
        self.page_number = page_number
        self.content = content

class PolicyParserService:
    def parse_text(self, text: str, page_number: int = 1) -> List[ParsedPolicySection]:
        sections: List[ParsedPolicySection] = []
        if not text:
            return sections

        lines = text.split("\n")
        current_section = "General Provision"
        current_clause = None
        buffer = []

        for line in lines:
            line_str = line.strip()
            # Section/heading detection (e.g. "Rule 144", "Chapter 6", "Section 4.1")
            heading_match = re.match(r"^(?:Rule|Chapter|Section|Clause)\s+(\d+[A-Z0-9.-]*)", line_str, re.IGNORECASE)
            if heading_match:
                if buffer:
                    sections.append(ParsedPolicySection(current_section, current_clause, page_number, "\n".join(buffer)))
                    buffer = []
                current_section = line_str
                current_clause = heading_match.group(1)
            else:
                buffer.append(line_str)

        if buffer:
            sections.append(ParsedPolicySection(current_section, current_clause, page_number, "\n".join(buffer)))

        return sections

policy_parser = PolicyParserService()
