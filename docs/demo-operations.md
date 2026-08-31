# Demo Operations & Management Guide

## Executing Master Seed Script
```bash
python backend/scripts/seed_demo_all.py
```

## Health Pre-flight Check
```bash
curl -X GET http://localhost:8000/api/v1/demo/health
```

## Running Scenario S via API
```bash
curl -X POST http://localhost:8000/api/v1/demo/scenarios/S/run \
  -H "Content-Type: application/json" \
  -d '{"mode": "FULL_RUN"}'
```

## Resetting Demo Environment
```bash
curl -X POST http://localhost:8000/api/v1/demo/reset
```
