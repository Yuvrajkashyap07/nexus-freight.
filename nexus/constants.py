"""Shared product constants and demo network reference data."""
from __future__ import annotations

from datetime import date

PRODUCT_NAME = "NEXUS Freight"
PRODUCT_TAGLINE = "AI-native logistics operations"
DEMO_AS_OF = date(2026, 11, 9)
CURRENCIES = ["USD", "EUR", "GBP", "AED", "SGD", "INR"]
MODES = ["Ocean FCL", "Ocean LCL", "Air", "Road", "Rail", "Multimodal"]
SHIPMENT_STATUSES = ["Draft", "Quoted", "Booked", "In transit", "Customs hold", "Exception", "Delivered", "Cancelled"]
QUOTE_STATUSES = ["Draft", "Sent", "Accepted", "Expired", "Rejected"]
EXCEPTION_STATUSES = ["Open", "In progress", "Resolved", "Escalated"]
SEVERITIES = ["Critical", "High", "Medium", "Low"]

# Geographic reference data uses real ports/cities; all shipment transactions are synthetic demo records.
PORTS = {
    "Shanghai, China": {"code": "CNSHA", "lat": 31.2304, "lon": 121.4737, "country": "China"},
    "Ningbo, China": {"code": "CNNGB", "lat": 29.8683, "lon": 121.5440, "country": "China"},
    "Singapore": {"code": "SGSIN", "lat": 1.2644, "lon": 103.8200, "country": "Singapore"},
    "Rotterdam, Netherlands": {"code": "NLRTM", "lat": 51.9244, "lon": 4.4777, "country": "Netherlands"},
    "Hamburg, Germany": {"code": "DEHAM", "lat": 53.5511, "lon": 9.9937, "country": "Germany"},
    "Antwerp, Belgium": {"code": "BEANR", "lat": 51.2194, "lon": 4.4025, "country": "Belgium"},
    "Los Angeles, USA": {"code": "USLAX", "lat": 33.7405, "lon": -118.2720, "country": "United States"},
    "New York, USA": {"code": "USNYC", "lat": 40.6840, "lon": -74.0060, "country": "United States"},
    "Long Beach, USA": {"code": "USLGB", "lat": 33.7542, "lon": -118.2165, "country": "United States"},
    "Dubai, UAE": {"code": "AEJEA", "lat": 24.9857, "lon": 55.0272, "country": "United Arab Emirates"},
    "Jebel Ali, UAE": {"code": "AEJEA", "lat": 24.9857, "lon": 55.0272, "country": "United Arab Emirates"},
    "Mumbai, India": {"code": "INBOM", "lat": 18.9388, "lon": 72.8354, "country": "India"},
    "Nhava Sheva, India": {"code": "INNSA", "lat": 18.9490, "lon": 72.9500, "country": "India"},
    "Busan, South Korea": {"code": "KRPUS", "lat": 35.1028, "lon": 129.0403, "country": "South Korea"},
    "Tokyo, Japan": {"code": "JPTYO", "lat": 35.4437, "lon": 139.6380, "country": "Japan"},
    "Santos, Brazil": {"code": "BRSSZ", "lat": -23.9608, "lon": -46.3336, "country": "Brazil"},
    "Felixstowe, UK": {"code": "GBFXT", "lat": 51.9540, "lon": 1.3511, "country": "United Kingdom"},
    "Sydney, Australia": {"code": "AUSYD", "lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    "Colombo, Sri Lanka": {"code": "LKCMB", "lat": 6.9497, "lon": 79.8428, "country": "Sri Lanka"},
    "Istanbul, Türkiye": {"code": "TRIST", "lat": 41.0082, "lon": 28.9784, "country": "Türkiye"},
}

CARRIERS = [
    "Atlas Ocean Lines", "BlueWave Logistics", "Meridian Global Freight",
    "Northstar Cargo", "Pacific Bridge Shipping", "AeroLink Express",
    "Continental Rail & Road", "Vertex Multimodal"
]

CUSTOMER_NAMES = [
    "Northstar Components GmbH", "Apex Retail Group", "Solstice Medical Supplies",
    "Harbor & Pine Trading", "Vertex Industrial Systems", "Meridian Foods Co.",
    "BluePeak Electronics", "Orion Home & Living", "Summit Auto Parts",
    "Evergreen Packaging Ltd", "Cobalt Construction Supply", "Nova Consumer Goods"
]

INCOTERMS = ["EXW", "FCA", "FOB", "CFR", "CIF", "DAP", "DPU", "DDP"]

MILESTONE_CATALOG = {
    "BOOKING_CONFIRMED": "Booking confirmed",
    "RECEIVED_FROM_SHIPPER": "Cargo received from shipper",
    "GATE_IN": "Gate-in at origin terminal",
    "LOADED_ON_VESSEL": "Loaded on vessel",
    "VESSEL_DEPARTED": "Vessel departed",
    "TRANSSHIPMENT": "Transshipment",
    "VESSEL_ARRIVED": "Vessel arrived",
    "DISCHARGED": "Discharged at destination",
    "CUSTOMS_RELEASED": "Customs released",
    "GATE_OUT": "Gate-out from destination terminal",
    "DELIVERED": "Delivered to consignee",
    "EMPTY_RETURNED": "Empty equipment returned",
}

DEMO_USERS = {
    "Operations Manager": {"role": "Operations Manager", "permissions": ["read", "write", "approve_quote", "resolve_exception"]},
    "Pricing Analyst": {"role": "Pricing Analyst", "permissions": ["read", "write_quote"]},
    "Finance Controller": {"role": "Finance Controller", "permissions": ["read", "finance"]},
    "Executive Viewer": {"role": "Executive Viewer", "permissions": ["read"]},
}
