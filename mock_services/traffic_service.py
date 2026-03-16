from fastapi import FastAPI
import random

app = FastAPI()

# Deliberately varied travel times to force interesting agent decisions
# Some fast chargers are far in traffic, some slow ones are close and clear
CHARGER_TRAFFIC = {
    "charger_001": {"minutes": 32, "congestion": "high"},    # ultra fast but far + heavy traffic
    "charger_002": {"minutes": 9,  "congestion": "low"},     # fast, close, clear — strong contender
    "charger_003": {"minutes": 16, "congestion": "medium"},  # cheap, medium distance
    "charger_004": {"minutes": 4,  "congestion": "low"},     # closest but slowest
    "charger_005": {"minutes": 7,  "congestion": "low"},     # fast, very close, only 1 slot
    "charger_006": {"minutes": 28, "congestion": "high"},    # ultra fast but far + congested
    "charger_007": {"minutes": 30, "congestion": "medium"},  # cheap but far and low rating
    "charger_008": {"minutes": 19, "congestion": "medium"},  # solid all round
    "charger_009": {"minutes": 13, "congestion": "low"},     # medium speed, close, clear
    "charger_010": {"minutes": 22, "congestion": "medium"},  # unavailable anyway
    "charger_011": {"minutes": 6,  "congestion": "low"},     # AC only
    "charger_012": {"minutes": 14, "congestion": "medium"},  # premium, great rating
    "charger_013": {"minutes": 8,  "congestion": "low"},     # cheap, close, low slots
    "charger_014": {"minutes": 17, "congestion": "medium"},  # wrong connector
    "charger_015": {"minutes": 45, "congestion": "high"},    # very far, heavy traffic
}


@app.get("/traffic/{charger_id}")
def get_traffic(charger_id: str):
    base = CHARGER_TRAFFIC.get(
        charger_id,
        {"minutes": 15, "congestion": "medium"}
    )
    return {
        "charger_id": charger_id,
        "estimated_minutes": base["minutes"] + random.randint(-2, 2),
        "congestion_level": base["congestion"],
        "route_available": True
    }