from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VEHICLE_SERVICE = "http://localhost:8001"
TRAFFIC_SERVICE = "http://localhost:8002"
ENERGY_SERVICE  = "http://localhost:8003"
BECKN_BPP       = "http://localhost:8004"
WALLET_SERVICE  = "http://localhost:8005"


# ── VEHICLE ───────────────────────────────────────────────────
@app.get("/tools/vehicle")
async def get_vehicle():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{VEHICLE_SERVICE}/vehicle/state")
        data = r.json()
    return {
        "battery_percent":  data.get("battery_percent"),
        "connector_type":   data.get("connector_type"),
        "charging_type":    data.get("charging_type"),
        "location":         data.get("location"),
        "range_km":         data.get("range_km")
    }


# ── TRAFFIC ───────────────────────────────────────────────────
@app.get("/tools/traffic/{charger_id}")
async def get_traffic(charger_id: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{TRAFFIC_SERVICE}/traffic/{charger_id}")
        return r.json()


# ── ENERGY ────────────────────────────────────────────────────
@app.get("/tools/energy-prices")
async def get_energy_prices():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{ENERGY_SERVICE}/energy/prices")
        return r.json()


# ── BECKN SEARCH ──────────────────────────────────────────────
class SearchRequest(BaseModel):
    connector_type: str
    charging_type:  str
    max_price:      float
    min_speed_kw:   float = 0


@app.post("/tools/beckn/search")
async def beckn_search(request: SearchRequest):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{BECKN_BPP}/beckn/search",
            json={
                "connector_type": request.connector_type,
                "charging_type":  request.charging_type,
                "max_price":      request.max_price,
                "min_speed_kw":   request.min_speed_kw
            }
        )
        data = r.json()

    chargers = data.get("chargers", [])

    # Score each charger
    for c in chargers:
        score = 0
        if c["speed_kw"] >= 100:  score += 30
        elif c["speed_kw"] >= 50: score += 15
        budget_remaining = request.max_price - c["price_per_kwh"]
        score += min(budget_remaining * 3, 30)
        score -= c["distance_km"] * 5
        c["initial_score"] = round(score, 1)

    chargers.sort(key=lambda x: x.get("initial_score", 0), reverse=True)

    return {
        "chargers":          chargers,
        "chargers_found":    len(chargers),
        "rejected_chargers": data.get("rejected_chargers", [])
    }


# ── BECKN SELECT ──────────────────────────────────────────────
class SelectRequest(BaseModel):
    charger_id: str


@app.post("/tools/beckn/select")
async def beckn_select(request: SelectRequest):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{BECKN_BPP}/beckn/select",
            json={"charger_id": request.charger_id}
        )
        return r.json()


# ── BECKN INIT ────────────────────────────────────────────────
class InitRequest(BaseModel):
    charger_id: str
    payment:    dict = {}


@app.post("/tools/beckn/init")
async def beckn_init(request: InitRequest):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{BECKN_BPP}/beckn/init",
            json={
                "charger_id": request.charger_id,
                "payment":    request.payment
            }
        )
        return r.json()


# ── BECKN CONFIRM ─────────────────────────────────────────────
class ConfirmRequest(BaseModel):
    order_id:       str
    charger_id:     str
    transaction_id: str = ""


@app.post("/tools/beckn/confirm")
async def beckn_confirm(request: ConfirmRequest):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{BECKN_BPP}/beckn/confirm",
            json={
                "order_id":       request.order_id,
                "charger_id":     request.charger_id,
                "transaction_id": request.transaction_id,
                "payment": {
                    "collected_by": "BAP",
                    "type":         "PRE-ORDER",
                    "status":       "PAID" if request.transaction_id else "NOT-PAID",
                    "params": {
                        "transaction_id": request.transaction_id,
                        "currency":       "INR"
                    }
                }
            }
        )
        return r.json()


# ── WALLET ────────────────────────────────────────────────────
@app.get("/tools/wallet/balance")
async def get_wallet_balance():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{WALLET_SERVICE}/wallet/balance")
        return r.json()


@app.post("/tools/wallet/topup")
async def wallet_topup():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{WALLET_SERVICE}/wallet/topup",
            params={"amount": 500}
        )
        return r.json()


@app.post("/tools/wallet/deduct")
async def wallet_deduct(request: dict):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{WALLET_SERVICE}/wallet/deduct",
            json=request
        )
        return r.json()