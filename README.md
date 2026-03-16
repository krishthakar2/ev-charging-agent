# EV Charging Agent

An autonomous agentic AI system for EV charging discovery and booking, 
built during my internship at Infosys.

The agent autonomously discovers, evaluates, scores, and books an EV 
charging session end to end without any human intervention using GPT-4o 
tool calling and the Beckn Protocol.

## What It Does

- Queries live vehicle telemetry, energy pricing, and traffic conditions
- Searches for chargers across the Beckn network matching user constraints
- Scores and ranks chargers across speed, price, distance, and availability
- Performs wallet-based payment following the Beckn payment declaration flow
- Confirms bookings end to end with transaction ID verification
- Streams real-time agent reasoning to the UI using Server-Sent Events
- Supports browse mode for assisted selection and auto mode for fully 
  autonomous booking

## Architecture

The system runs across six independent microservices:

- Vehicle Service — battery level, connector type, location
- Traffic Service — live congestion and travel time
- Energy Service — real-time grid pricing and peak hour status
- Beckn BPP — charger network with search, select, init, confirm flow
- Wallet Service — balance management and payment deduction
- MCP Gateway — central gateway mediating all agent-to-service communication

## Tech Stack

- Python, FastAPI, Uvicorn
- GPT-4o tool calling
- Beckn Protocol / Unified Energy Interface
- Model Context Protocol (MCP)
- Server-Sent Events
- Pydantic, REST APIs

## Key Technical Decisions

**MCP Gateway** — the agent never calls any data source directly. All 
requests are mediated through the MCP server. This means swapping a mock 
service for a real API requires changing one URL in one file.

**Dual Constraint Enforcement** — price and speed filters are enforced at 
both the BPP data layer and the agent prompt layer independently. The 
system cannot book outside the user's constraints regardless of agent 
reasoning.

**Beckn Payment Flow** — the agent declares payment intent in the init 
message, deducts from the wallet to receive a transaction ID, and passes 
that ID in the confirm message. The BPP rejects any confirmation without 
a valid transaction ID.

## Running the Project

Start all six services in separate terminals:
```bash
uvicorn mock_services.vehicle_service:app --port 8001
uvicorn mock_services.traffic_service:app --port 8002
uvicorn mock_services.energy_service:app --port 8003
uvicorn mock_services.beckn_bpp:app --port 8004
uvicorn mock_services.wallet_service:app --port 8005
uvicorn mcp_server.mcp_server:app --port 8000
uvicorn main:app --port 8080
```

Then open http://localhost:8080 in your browser.

## Built During

Infosys Internship — 2026
```
