# Policy Ingestion Pipeline

## Overview
Ingests policy documents (PDFs/manuals) into `policy_sources`, `policy_versions`, and `policy_chunks`.

## Pipeline Steps
1. **Document Validation & SHA-256 Hashing**: Calculates document checksum to avoid re-ingesting unchanged versions.
2. **Parsing**: Identifies rules, chapters, and section headings.
3. **Semantic Chunking**: Chunks text maintaining section hierarchy (~500 characters with 50 character overlap).
4. **Vector Embedding Generation**: Generates embeddings and stores in vector column (JSON string / pgvector).
