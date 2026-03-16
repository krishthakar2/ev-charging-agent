from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

wallet = {
    "balance": 500.00,
    "currency": "INR",
    "transactions": []
}


@app.get("/wallet/balance")
def get_balance():
    return {
        "balance": wallet["balance"],
        "currency": wallet["currency"],
        "transaction_count": len(wallet["transactions"])
    }


@app.post("/wallet/topup")
def top_up(amount: float = 500.0):
    wallet["balance"] = round(wallet["balance"] + amount, 2)
    wallet["transactions"].append({
        "id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
        "type": "topup",
        "amount": amount,
        "balance_after": wallet["balance"],
        "timestamp": datetime.now().isoformat()
    })
    return {
        "success": True,
        "added": amount,
        "balance": wallet["balance"],
        "message": f"₹{amount:.0f} added to wallet"
    }


class DeductRequest(BaseModel):
    amount: float
    order_id: str


@app.post("/wallet/deduct")
def deduct(request: DeductRequest):
    if wallet["balance"] < request.amount:
        return {
            "success": False,
            "balance": wallet["balance"],
            "shortfall": round(request.amount - wallet["balance"], 2),
            "message": f"Insufficient balance. Need ₹{request.amount:.0f}, have ₹{wallet['balance']:.0f}"
        }
    wallet["balance"] = round(wallet["balance"] - request.amount, 2)
    txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    wallet["transactions"].append({
        "id": txn_id,
        "type": "debit",
        "amount": request.amount,
        "order_id": request.order_id,
        "balance_after": wallet["balance"],
        "timestamp": datetime.now().isoformat()
    })
    return {
        "success": True,
        "transaction_id": txn_id,
        "amount_charged": request.amount,
        "balance_after": wallet["balance"],
        "message": f"₹{request.amount:.0f} charged successfully"
    }


@app.get("/wallet/transactions")
def get_transactions():
    return {
        "transactions": wallet["transactions"],
        "total": len(wallet["transactions"])
    }