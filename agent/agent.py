import os
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MCP_SERVER = "http://localhost:8000"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_vehicle_state",
            "description": "Get the current EV state: battery, connector type, charging type, location. Always call this first.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_energy_prices",
            "description": "Get current grid energy prices and peak hour status.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_traffic",
            "description": "Get travel time and congestion to a specific charger.",
            "parameters": {
                "type": "object",
                "properties": {
                    "charger_id": {
                        "type": "string",
                        "description": "Charger ID e.g. charger_001"
                    }
                },
                "required": ["charger_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "beckn_search",
            "description": "Search Beckn network for chargers matching all criteria strictly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "connector_type": {"type": "string"},
                    "charging_type":  {"type": "string"},
                    "max_price": {
                        "type": "number",
                        "description": "Hard maximum price per kWh — reject anything above this"
                    },
                    "min_speed_kw": {
                        "type": "number",
                        "description": "Hard minimum charging speed in kW — reject anything below this"
                    }
                },
                "required": ["connector_type", "charging_type", "max_price", "min_speed_kw"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_wallet_balance",
            "description": "Get the user's current wallet balance. Call this after picking the best charger but BEFORE beckn_select. Estimated cost = price_per_kwh x 20. If balance < estimated cost, stop immediately — do NOT call beckn_select. Tell the user exactly how much they need to top up.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "beckn_select",
            "description": "Select a charger and get confirmed price quote. Only call this AFTER confirming wallet has sufficient balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "charger_id": {"type": "string"}
                },
                "required": ["charger_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "beckn_init",
            "description": "Initialise the booking order. Include estimated_amount as price_per_kwh x 20.",
            "parameters": {
                "type": "object",
                "properties": {
                    "charger_id":        {"type": "string"},
                    "estimated_amount": {
                        "type": "number",
                        "description": "Estimated session cost in INR — price_per_kwh x 20"
                    }
                },
                "required": ["charger_id", "estimated_amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wallet_deduct",
            "description": "Deduct session cost from wallet AFTER beckn_init succeeds. Use order_id from beckn_init. Returns transaction_id needed for beckn_confirm.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Amount to deduct in INR"
                    },
                    "order_id": {
                        "type": "string",
                        "description": "Order ID from beckn_init"
                    }
                },
                "required": ["amount", "order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "beckn_confirm",
            "description": "Confirm and complete the booking. Requires transaction_id from wallet_deduct. Do not call this without a valid transaction_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id":       {"type": "string"},
                    "charger_id":     {"type": "string"},
                    "transaction_id": {
                        "type": "string",
                        "description": "Transaction ID from wallet_deduct"
                    }
                },
                "required": ["order_id", "charger_id", "transaction_id"]
            }
        }
    }
]


async def execute_tool(tool_name: str, tool_args: dict):
    async with httpx.AsyncClient(timeout=10.0) as http:
        if tool_name == "get_vehicle_state":
            r = await http.get(f"{MCP_SERVER}/tools/vehicle")
            return r.json()
        elif tool_name == "get_energy_prices":
            r = await http.get(f"{MCP_SERVER}/tools/energy-prices")
            return r.json()
        elif tool_name == "get_traffic":
            r = await http.get(
                f"{MCP_SERVER}/tools/traffic/{tool_args['charger_id']}"
            )
            return r.json()
        elif tool_name == "beckn_search":
            r = await http.post(
                f"{MCP_SERVER}/tools/beckn/search",
                json=tool_args
            )
            return r.json()
        elif tool_name == "get_wallet_balance":
            r = await http.get(f"{MCP_SERVER}/tools/wallet/balance")
            return r.json()
        elif tool_name == "beckn_select":
            r = await http.post(
                f"{MCP_SERVER}/tools/beckn/select",
                json=tool_args
            )
            return r.json()
        elif tool_name == "beckn_init":
            r = await http.post(
                f"{MCP_SERVER}/tools/beckn/init",
                json={
                    "charger_id": tool_args["charger_id"],
                    "payment": {
                        "collected_by": "BAP",
                        "type":         "PRE-ORDER",
                        "status":       "NOT-PAID",
                        "params": {
                            "amount":         str(tool_args.get("estimated_amount", 280)),
                            "currency":       "INR",
                            "transaction_id": ""
                        }
                    }
                }
            )
            return r.json()
        elif tool_name == "wallet_deduct":
            r = await http.post(
                f"{MCP_SERVER}/tools/wallet/deduct",
                json=tool_args
            )
            return r.json()
        elif tool_name == "beckn_confirm":
            r = await http.post(
                f"{MCP_SERVER}/tools/beckn/confirm",
                json=tool_args
            )
            return r.json()
        else:
            return {"error": f"Unknown tool: {tool_name}"}


BROWSE_PROMPT = """
You are an EV charging assistant helping the user find the right charger.

Follow these steps in order:
1. Call get_vehicle_state
2. Call get_energy_prices
3. Call beckn_search using EXACTLY the connector_type and charging_type the USER
   specified in their request. Never use the vehicle connector or charging type.
   Use user's max_price and min_speed_kw.
4. If chargers_found is 0 — stop and explain why using rejected_chargers
5. If chargers found — call get_traffic for every single charger
6. Output the charger list

After all tool calls output ONLY one of:

If chargers found:
CHARGER_LIST_START
[array of charger objects]
CHARGER_LIST_END

If nothing matched:
NO_CHARGERS_START
{"message": "explanation", "rejected": [{"name": "...", "reasons": ["..."]}], "suggestions": ["..."]}
NO_CHARGERS_END
"""

AUTO_PROMPT = """
You are an autonomous EV charging agent. Find AND book the best charger.

Follow this exact sequence:
1.  get_vehicle_state
2.  get_energy_prices
3.  beckn_search — use EXACTLY the connector_type and charging_type from the
    USER's request. Never use the vehicle connector or charging type.
    Use user's max_price and min_speed_kw.
4.  If chargers_found is 0 — stop, explain why, do not book
5.  Call get_traffic for every qualifying charger
6.  Score every charger:
    - Speed (HIGH weight): faster is better above minimum
    - Price (HIGH weight): lower is better within budget
    - Available slots (CRITICAL): 1 slot = heavy penalty, near-disqualifier
      unless no other charger within 15 minutes has 2+ slots
    - Travel time (MEDIUM weight): shorter is better
    - Rating (LOW weight): tiebreaker only
7.  Pick the overall winner
8.  get_wallet_balance
    - Estimated cost = winner's price_per_kwh x 20
    - If wallet balance < estimated cost:
      STOP. Do not call beckn_select.
      Tell the user the exact shortfall and to top up.
9.  beckn_select (winner charger_id)
10. beckn_init (charger_id, estimated_amount = price_per_kwh x 20)
11. wallet_deduct (amount = estimated_amount, order_id from beckn_init)
12. beckn_confirm (order_id, charger_id, transaction_id from wallet_deduct)
13. Write reasoning paragraph including:
    - Which charger won and why with specific numbers
    - Top 2 runners up and why they lost
    - Amount charged from wallet and remaining balance
    - Whether peak hours affected the recommendation

CRITICAL RULES:
- Never book above max price or below min speed
- Never book if wallet balance is insufficient
- Always pass transaction_id from wallet_deduct into beckn_confirm
"""


async def run_agent(user_request: str, mode: str = "browse"):
    system_prompt = BROWSE_PROMPT if mode == "browse" else AUTO_PROMPT

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_request}
    ]

    yield f"🚗 Starting agent in {'browse' if mode == 'browse' else 'auto-book'} mode...\n\n"

    search_results   = []
    rejected_results = []
    traffic_results  = {}
    reasoning_captured = False

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # ── FINAL RESPONSE ────────────────────────────────────
        if not message.tool_calls:
            final_text = (message.content or "").strip()

            if mode == "browse":
                if "NO_CHARGERS_START" in final_text and "NO_CHARGERS_END" in final_text:
                    try:
                        start = final_text.index("NO_CHARGERS_START") + len("NO_CHARGERS_START")
                        end   = final_text.index("NO_CHARGERS_END")
                        data  = json.loads(final_text[start:end].strip())
                        yield f"NO_CHARGERS:{json.dumps(data)}\n"
                    except Exception:
                        yield f"✅ {final_text}\n"
                    break

                if search_results:
                    charger_list = []
                    for charger in search_results:
                        traffic = traffic_results.get(charger["id"], {})
                        charger_list.append({
                            "id":              charger["id"],
                            "name":            charger["name"],
                            "operator":        charger["operator"],
                            "address":         charger["location"]["address"],
                            "speed_kw":        charger["speed_kw"],
                            "price_per_kwh":   charger["price_per_kwh"],
                            "connector_type":  charger["connector_type"],
                            "charging_type":   charger["charging_type"],
                            "distance_km":     charger["distance_km"],
                            "travel_minutes":  traffic.get("estimated_minutes", "N/A"),
                            "congestion":      traffic.get("congestion_level", "unknown"),
                            "available_slots": charger.get("available_slots", 1),
                            "total_slots":     charger.get("total_slots", 1),
                            "rating":          charger.get("rating", 4.0),
                            "amenities":       charger.get("amenities", []),
                            "available":       charger["available"]
                        })
                    yield f"✅ Found {len(charger_list)} chargers matching your criteria.\n"
                    yield f"CHARGER_LIST:{json.dumps(charger_list)}\n"
                else:
                    yield f"NO_CHARGERS:{json.dumps({'message': final_text or 'No chargers matched.', 'rejected': rejected_results, 'suggestions': ['Raise your maximum price per kWh', 'Lower your minimum speed requirement', 'Try a different connector type']})}\n"

            else:
                # AUTO MODE
                if not search_results:
                    yield f"HIDE_REASONING:\n"
                    yield f"NO_CHARGERS:{json.dumps({'message': final_text or 'No chargers matched.', 'rejected': rejected_results, 'suggestions': ['Raise your maximum price per kWh', 'Lower your minimum speed requirement', 'Try a different connector type']})}\n"
                elif final_text and not reasoning_captured and len(final_text) > 30:
                    reasoning_captured = True
                    yield f"AGENT_REASONING:{final_text}\n"
                elif final_text:
                    yield f"✅ {final_text}\n"

            break

        # ── INLINE REASONING ──────────────────────────────────
        if (
            mode == "auto"
            and message.content
            and message.content.strip()
            and len(message.content.strip()) > 30
            and not reasoning_captured
            and search_results
        ):
            reasoning_captured = True
            yield f"AGENT_REASONING:{message.content.strip()}\n"

        # ── ADD TO CONVERSATION ───────────────────────────────
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id":   tc.id,
                    "type": "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # ── EXECUTE TOOLS ─────────────────────────────────────
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            yield f"🔧 Calling tool: {tool_name}\n"

            result = await execute_tool(tool_name, tool_args)

            if tool_name == "beckn_search":
                search_results   = result.get("chargers", [])
                rejected_results = result.get("rejected_chargers", [])

            if tool_name == "get_traffic":
                charger_id = tool_args.get("charger_id")
                if charger_id:
                    traffic_results[charger_id] = result

            if tool_name == "get_wallet_balance":
                yield f"💳 Wallet balance: ₹{result.get('balance', 0):.2f}\n"

            for line in json.dumps(result, indent=2).split('\n'):
                yield f"📦 {line}\n"
            yield "\n"

            if tool_name == "wallet_deduct":
                if result.get("success"):
                    yield f"💳 ₹{result.get('amount_charged')} charged — Balance: ₹{result.get('balance_after', 0):.2f}\n"
                    yield f"WALLET_UPDATE:{json.dumps(result)}\n"
                else:
                    yield f"❌ {result.get('message')}\n"
                    yield f"INSUFFICIENT_FUNDS:{json.dumps(result)}\n"

            if tool_name == "beckn_confirm" and result.get("status") == "CONFIRMED":
                yield f"BOOKING_DATA:{json.dumps(result)}\n"

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      json.dumps(result)
            })


async def book_charger(charger_id: str):
    yield f" Booking charger {charger_id}...\n\n"

    messages = [
        {
            "role": "system",
            "content": """You are an EV booking agent. The user has chosen a charger.
Follow this exact sequence:
1. get_wallet_balance — estimated cost is price_per_kwh x 20.
   If insufficient stop and explain the exact shortfall.
2. beckn_select
3. beckn_init (include estimated_amount = price_per_kwh x 20)
4. wallet_deduct (amount = estimated_amount, order_id from beckn_init)
5. beckn_confirm (order_id, charger_id, transaction_id from wallet_deduct)
Never skip the wallet check. Never call beckn_confirm without a transaction_id."""
        },
        {
            "role": "user",
            "content": f"Book charger ID: {charger_id}"
        }
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if not message.tool_calls:
            yield f" {message.content}\n"
            break

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id":   tc.id,
                    "type": "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            yield f"🔧 Calling tool: {tool_name}\n"
            result = await execute_tool(tool_name, tool_args)

            if tool_name == "get_wallet_balance":
                yield f"💳 Wallet balance: ₹{result.get('balance', 0):.2f}\n"

            for line in json.dumps(result, indent=2).split('\n'):
                yield f"📦 {line}\n"
            yield "\n"

            if tool_name == "wallet_deduct":
                if result.get("success"):
                    yield f"💳 ₹{result.get('amount_charged')} charged — Balance: ₹{result.get('balance_after', 0):.2f}\n"
                    yield f"WALLET_UPDATE:{json.dumps(result)}\n"
                else:
                    yield f"❌ {result.get('message')}\n"
                    yield f"INSUFFICIENT_FUNDS:{json.dumps(result)}\n"

            if tool_name == "beckn_confirm" and result.get("status") == "CONFIRMED":
                yield f"BOOKING_DATA:{json.dumps(result)}\n"

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      json.dumps(result)
            })