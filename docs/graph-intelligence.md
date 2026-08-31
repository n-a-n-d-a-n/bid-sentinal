# Graph Intelligence Engine

## Overview
Stores procurement entity network in PostgreSQL (`graph_entities` & `graph_relationships`) and performs in-memory analytics using NetworkX.

## Entity Types
- `BIDDER`, `ORGANIZATION`, `PERSON`, `TENDER`, `BID`, `DOCUMENT`, `PAN`, `GSTIN`, `CIN`, `UDYAM`, `ADDRESS`, `BANK_ACCOUNT`, `DIRECTOR`.

## Relationship Types
- `BIDDER_SUBMITTED_BID`, `BIDDER_HAS_PAN`, `BIDDER_HAS_GSTIN`, `BIDDER_HAS_ADDRESS`, `BIDDER_HAS_DIRECTOR`, `PERSON_DIRECTOR_OF`, `BIDDER_WON_TENDER`, `DOCUMENT_SUPPORTS_BIDDER`, `ENTITY_MATCH`, `ENTITY_POSSIBLE_MATCH`.

## Network Signals
- `MULTIPLE_BIDDERS_SHARED_ADDRESS`
- `MULTIPLE_BIDDERS_SHARED_DIRECTOR`
- `MULTIPLE_BIDDERS_SHARED_BANK_ACCOUNT`
- `CLUSTERED_BIDDER_NETWORK`
- `COMMON_CONTROL_ENTITY`

## Neutral Terminology Rule
The graph engine identifies signals. It never declares "collusion" or "fraud" automatically. Final determination belongs to the Procurement Officer.
