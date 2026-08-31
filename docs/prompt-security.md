# Prompt Security & Injection Defense

## Threat Model
Policy PDFs uploaded by external parties are untrusted input. They may contain adversarial text such as "Ignore previous instructions" or "Grant admin access".

## Security Controls
1. **Input Sanitization**: Input filter strips known prompt injection patterns.
2. **Treat Policy Text as Data**: Policy passages are passed inside strictly delimited data blocks.
3. **System Prompt Authority**: The system prompt remains authoritative over all retrieved content.
