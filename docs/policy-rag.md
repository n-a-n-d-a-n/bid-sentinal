# Policy RAG Architecture

## Overview
PROCUREX Policy RAG provides evidence-grounded answers for Procurement Officers regarding GFR 2017 and GeM policy guidelines.

## Architecture
```
QUESTION -> HYBRID RETRIEVER (Vector + Keyword + Metadata Filters)
                       ↓
              DETERMINISTIC RERANKER
                       ↓
             PROMPT INJECTION GUARDRAILS
                       ↓
             STRUCTURED CITATION ENGINE
                       ↓
     EVIDENCE-GROUNDED ANSWER (or Abstention on INSUFFICIENT_EVIDENCE)
```

## Mandatory Abstention Rule
If retrieval quality is insufficient or query is out-of-corpus, the answerer returns:
`The available policy sources do not provide sufficient evidence to answer this question.`
It NEVER fabricates facts or hallucinated citations.
