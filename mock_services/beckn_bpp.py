from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHARGERS = [
    {
        "id": "charger_001",
        "name": "E.ON 1",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9352, "lng": 77.6245, "address": "E.ON Station 1, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 350,
        "price_per_kwh": 22.0,
        "available": True,
        "distance_km": 8.5,
        "amenities": ["Lounge", "Wi-Fi", "Restrooms", "Cafe"],
        "rating": 4.9,
        "total_slots": 10,
        "available_slots": 8
    },
    {
        "id": "charger_002",
        "name": "E.ON 2",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9784, "lng": 77.6408, "address": "E.ON Station 2, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 150,
        "price_per_kwh": 14.0,
        "available": True,
        "distance_km": 2.1,
        "amenities": ["Covered parking", "Security", "24/7"],
        "rating": 4.7,
        "total_slots": 8,
        "available_slots": 5
    },
    {
        "id": "charger_003",
        "name": "E.ON 3",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9121, "lng": 77.6446, "address": "E.ON Station 3, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 100,
        "price_per_kwh": 9.5,
        "available": True,
        "distance_km": 3.4,
        "amenities": ["Open air", "ATM nearby"],
        "rating": 4.2,
        "total_slots": 4,
        "available_slots": 2
    },
    {
        "id": "charger_004",
        "name": "E.ON 4",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9308, "lng": 77.5831, "address": "E.ON Station 4, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 22,
        "price_per_kwh": 7.0,
        "available": True,
        "distance_km": 0.8,
        "amenities": ["Street parking", "Convenience store"],
        "rating": 3.8,
        "total_slots": 2,
        "available_slots": 1
    },
    {
        "id": "charger_005",
        "name": "E.ON 5",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9751, "lng": 77.6099, "address": "E.ON Station 5, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 120,
        "price_per_kwh": 12.0,
        "available": True,
        "distance_km": 1.3,
        "amenities": ["Metro access", "Covered", "Security"],
        "rating": 4.4,
        "total_slots": 3,
        "available_slots": 1
    },
    {
        "id": "charger_006",
        "name": "E.ON 6",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9698, "lng": 77.7499, "address": "E.ON Station 6, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 200,
        "price_per_kwh": 13.5,
        "available": True,
        "distance_km": 6.2,
        "amenities": ["Food court", "Parking", "24/7", "Wi-Fi"],
        "rating": 4.6,
        "total_slots": 12,
        "available_slots": 9
    },
    {
        "id": "charger_007",
        "name": "E.ON 7",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9255, "lng": 77.5468, "address": "E.ON Station 7, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 75,
        "price_per_kwh": 10.0,
        "available": True,
        "distance_km": 7.1,
        "amenities": ["CCTV", "Open air"],
        "rating": 3.6,
        "total_slots": 2,
        "available_slots": 1
    },
    {
        "id": "charger_008",
        "name": "E.ON 8",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9591, "lng": 77.6974, "address": "E.ON Station 8, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 90,
        "price_per_kwh": 11.5,
        "available": True,
        "distance_km": 4.2,
        "amenities": ["Supermarket", "Parking", "Restrooms"],
        "rating": 4.3,
        "total_slots": 6,
        "available_slots": 4
    },
    {
        "id": "charger_009",
        "name": "E.ON 9",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9916, "lng": 77.5530, "address": "E.ON Station 9, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 60,
        "price_per_kwh": 11.0,
        "available": True,
        "distance_km": 2.8,
        "amenities": ["Petrol station", "Air pump", "Shop"],
        "rating": 4.0,
        "total_slots": 4,
        "available_slots": 3
    },
    {
        "id": "charger_010",
        "name": "E.ON 10",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.8399, "lng": 77.6770, "address": "E.ON Station 10, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 150,
        "price_per_kwh": 13.0,
        "available": False,
        "distance_km": 5.0,
        "amenities": ["Tech park", "Cafeteria", "Wi-Fi"],
        "rating": 4.5,
        "total_slots": 6,
        "available_slots": 0
    },
    {
        "id": "charger_011",
        "name": "E.ON 11",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9450, "lng": 77.5900, "address": "E.ON Station 11, Bengaluru"},
        "connector_type": "Type 2",
        "charging_type": "AC",
        "speed_kw": 22,
        "price_per_kwh": 6.5,
        "available": True,
        "distance_km": 1.5,
        "amenities": ["Residential", "Overnight charging"],
        "rating": 4.1,
        "total_slots": 4,
        "available_slots": 3
    },
    {
        "id": "charger_012",
        "name": "E.ON 12",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9600, "lng": 77.6300, "address": "E.ON Station 12, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 180,
        "price_per_kwh": 18.0,
        "available": True,
        "distance_km": 3.1,
        "amenities": ["Premium lounge", "Valet", "Cafe", "Wi-Fi", "Restrooms"],
        "rating": 5.0,
        "total_slots": 8,
        "available_slots": 6
    },
    {
        "id": "charger_013",
        "name": "E.ON 13",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9200, "lng": 77.6100, "address": "E.ON Station 13, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 50,
        "price_per_kwh": 9.0,
        "available": True,
        "distance_km": 1.9,
        "amenities": ["Street level", "24/7"],
        "rating": 3.9,
        "total_slots": 2,
        "available_slots": 1
    },
    {
        "id": "charger_014",
        "name": "E.ON 14",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.9800, "lng": 77.5700, "address": "E.ON Station 14, Bengaluru"},
        "connector_type": "CHAdeMO",
        "charging_type": "DC",
        "speed_kw": 100,
        "price_per_kwh": 12.0,
        "available": True,
        "distance_km": 4.0,
        "amenities": ["Parking", "Security"],
        "rating": 4.0,
        "total_slots": 3,
        "available_slots": 2
    },
    {
        "id": "charger_015",
        "name": "E.ON 15",
        "operator": "E.ON EV Charging",
        "location": {"lat": 12.8500, "lng": 77.7000, "address": "E.ON Station 15, Bengaluru"},
        "connector_type": "CCS2",
        "charging_type": "DC",
        "speed_kw": 125,
        "price_per_kwh": 13.0,
        "available": True,
        "distance_km": 12.0,
        "amenities": ["Large hub", "Multiple operators", "Food", "Restrooms"],
        "rating": 4.5,
        "total_slots": 20,
        "available_slots": 15
    }
]


class SearchRequest(BaseModel):
    connector_type: str
    charging_type:  str
    max_price:      float
    min_speed_kw:   float = 0
    location:       dict  = {}


class SelectRequest(BaseModel):
    charger_id: str


class InitRequest(BaseModel):
    charger_id: str
    payment:    dict = {}


class ConfirmRequest(BaseModel):
    order_id:       str
    charger_id:     str
    transaction_id: str  = ""
    payment:        dict = {}


@app.post("/beckn/search")
def beckn_search(request: SearchRequest):
    matching = []
    rejected = []

    for c in CHARGERS:
        reasons = []

        if c["connector_type"] != request.connector_type:
            reasons.append(f"connector is {c['connector_type']}, need {request.connector_type}")

        if c["charging_type"] != request.charging_type:
            reasons.append(f"charging type is {c['charging_type']}, need {request.charging_type}")

        if not c["available"]:
            reasons.append("currently unavailable")

        if c["price_per_kwh"] > request.max_price:
            reasons.append(f"price ₹{c['price_per_kwh']}/kWh exceeds budget of ₹{request.max_price}/kWh")

        if request.min_speed_kw and c["speed_kw"] < request.min_speed_kw:
            reasons.append(f"speed {c['speed_kw']}kW is below minimum {request.min_speed_kw}kW")

        if reasons:
            rejected.append({"name": c["name"], "reasons": reasons})
        else:
            matching.append(c)

    return {
        "action":            "on_search",
        "chargers":          matching,
        "total_found":       len(matching),
        "rejected_chargers": rejected,
        "search_criteria": {
            "connector_type":    request.connector_type,
            "charging_type":     request.charging_type,
            "max_price_per_kwh": request.max_price,
            "min_speed_kw":      request.min_speed_kw
        }
    }


@app.post("/beckn/select")
def beckn_select(request: SelectRequest):
    charger = next((c for c in CHARGERS if c["id"] == request.charger_id), None)
    if not charger:
        return {"error": "Charger not found"}
    return {
        "action":                  "on_select",
        "charger":                 charger,
        "quoted_price_per_kwh":    charger["price_per_kwh"],
        "estimated_session_cost":  round(charger["price_per_kwh"] * 20, 2),
        "slot_held_until":         "10 minutes"
    }


@app.post("/beckn/init")
def beckn_init(request: InitRequest):
    charger = next((c for c in CHARGERS if c["id"] == request.charger_id), None)
    if not charger:
        return {"error": "Charger not found"}

    order_id         = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    payment          = request.payment
    estimated_amount = payment.get("params", {}).get("amount", str(round(charger["price_per_kwh"] * 20, 2)))

    return {
        "action":     "on_init",
        "order_id":   order_id,
        "charger_id": request.charger_id,
        "charger_name": charger["name"],
        "status":     "PAYMENT_PENDING",
        "payment": {
            "collected_by": payment.get("collected_by", "BAP"),
            "type":         payment.get("type", "PRE-ORDER"),
            "status":       "NOT-PAID",
            "params": {
                "amount":         estimated_amount,
                "currency":       "INR",
                "transaction_id": ""
            }
        },
        "message": "Order initialised. Complete payment to confirm booking."
    }


@app.post("/beckn/confirm")
def beckn_confirm(request: ConfirmRequest):
    charger = next((c for c in CHARGERS if c["id"] == request.charger_id), None)
    if not charger:
        return {"error": "Charger not found"}

    # Get transaction_id from top-level field or nested payment params
    transaction_id = (
        request.transaction_id
        or request.payment.get("params", {}).get("transaction_id", "")
    )

    payment_status = request.payment.get("status", "")

    # Block confirmation if no transaction ID
    if not transaction_id:
        return {
            "status":  "PAYMENT_FAILED",
            "message": "Cannot confirm — no transaction ID provided. Complete wallet payment first."
        }

    return {
        "action":               "on_confirm",
        "order_id":             request.order_id,
        "status":               "CONFIRMED",
        "transaction_id":       transaction_id,
        "payment_status":       "PAID",
        "charger_name":         charger["name"],
        "charger_address":      charger["location"]["address"],
        "operator":             charger["operator"],
        "connector_type":       charger["connector_type"],
        "charging_type":        charger["charging_type"],
        "speed_kw":             charger["speed_kw"],
        "price_per_kwh":        charger["price_per_kwh"],
        "available_slots":      charger["available_slots"],
        "total_slots":          charger["total_slots"],
        "amenities":            charger["amenities"],
        "rating":               charger["rating"],
        "distance_km":          charger["distance_km"],
        "session_id":           f"SES-{uuid.uuid4().hex[:8].upper()}",
        "confirmed_at":         datetime.now().isoformat(),
        "estimated_cost_20kwh": round(charger["price_per_kwh"] * 20, 2),
        "message":              "Your charger is reserved. Please arrive within 10 minutes."
    }