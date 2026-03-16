from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/vehicle/state")
def get_vehicle_state():
    return {
        "battery_percent": random.randint(10, 30),
        "connector_type": "CCS2",
        "charging_type": "DC",
        "location": {
            "lat": 12.9716,
            "lng": 77.5946,
            "address": "Koramangala, Bengaluru"
        },
        "range_km": random.randint(20, 60),
        "vehicle_id": "KA-01-EV-2024"
    }