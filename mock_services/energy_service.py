from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/energy/prices")
def get_energy_prices():
    hour = datetime.now().hour
    is_peak = 8 <= hour <= 11 or 18 <= hour <= 22

    return {
        "is_peak_hours": is_peak,
        "grid_load": "high" if is_peak else "normal",
        "base_price_per_kwh": 12.5 if is_peak else 9.0,
        "currency": "INR",
        "timestamp": datetime.now().isoformat(),
        "recommendation": "Consider waiting for off-peak hours" if is_peak else "Good time to charge"
    }