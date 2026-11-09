# Standards and integration mapping

## Important distinction

NEXUS defines its own canonical internal data model. The mapping below is an implementation guide only. It is not a claim of certification or complete conformity to DCSA or IATA standards. Implementers must use the current specifications, security profiles, code lists and conformance tools from the standards organisations.

## Ocean: DCSA Track & Trace

DCSA standardises shared shipment, transport, equipment, IoT and reefer event semantics across carriers, terminals, shippers and visibility platforms.

| NEXUS internal example | Integration intent | Notes |
|---|---|---|
| BOOKING_CONFIRMED | Shipment event | Link booking reference and shipment identity |
| GATE_IN | Equipment / transport event | Retain terminal, equipment and event time |
| LOADED_ON_VESSEL | Transport / equipment event | Preserve vessel/voyage and transport-call references |
| VESSEL_DEPARTED | Transport event | Departure event time and location |
| TRANSSHIPMENT | Transport event | Model each leg / port call; do not overwrite prior leg |
| VESSEL_ARRIVED | Transport event | Arrival and actual time |
| DISCHARGED | Equipment / transport event | Distinguish vessel arrival from discharge |
| CUSTOMS_RELEASED | Regulatory / business milestone | May originate outside a carrier event API |
| GATE_OUT | Equipment event | Retain release / pickup references |
| DELIVERED | Shipment event | Proof-of-delivery evidence and recipient |
| EMPTY_RETURNED | Equipment event | Container lifecycle closure |

Useful fields: event ID, event type/code, event classifier, event time, receive time, location, transport call, equipment reference, shipment reference, source provider, raw payload hash and schema version.

## Air cargo: IATA ONE Record

IATA ONE Record is a data-sharing standard based on a common digital shipment record and secured web API. The endorsed July 2026 release includes Ontology 3.3.0 and API 2.3.0.

NEXUS should map air shipment, piece, handling, transport leg, party, location and document references to the appropriate ONE Record objects/properties. Use the IATA-maintained ontology and API docs; do not invent JSON-LD predicates from this illustrative mapping.

## Partner adapter contract

Each adapter should implement:

```python
class PartnerAdapter:
    def authenticate(self) -> None: ...
    def fetch_events(self, cursor: str | None = None) -> list[dict]: ...
    def normalise_event(self, raw_event: dict) -> dict: ...
    def submit_booking(self, booking: dict, idempotency_key: str) -> dict: ...
    def health_check(self) -> dict: ...
```

Not every partner supports every operation. `submit_booking` is optional and must be behind an approval control.

## Idempotency and replay

- Prefer partner-provided immutable event identifiers.
- If unavailable, derive a stable key from provider + entity reference + event code + event time + location + payload hash.
- Store raw payload with receipt time and provider account identity.
- Quarantine malformed or unmapped events; do not silently discard them.
- Permit replay after a mapping fix while retaining original receipt and replay metadata.
- Record corrections as additional events with a supersedes reference.

## Reference data

Use maintained port/location code sources. Store UN/LOCODE for ports/places and IATA location codes where relevant. Do not treat free-text place names as unique identifiers. Timezone conversion must be location-aware and preserve the original partner timestamp/offset.
