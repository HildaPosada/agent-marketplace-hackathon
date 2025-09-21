from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uvicorn
import os
import json

# Solana Devnet client
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams

# Use solders for keys + pubkeys
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Import our enhanced marketplace with Coral integration
from agent_marketplace import AgentMarketplace, WorkflowRequest
from coral_integration import CoralMarketplaceIntegration

app = FastAPI(
    title="🏪 Agent Marketplace - Coral Protocol Integration",
    description="Rent specialized AI agents with Solana payments powered by Coral Protocol",
    version="2.0.0"
)

# -------------------
# Middleware
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# Marketplace + Coral
# -------------------
marketplace = AgentMarketplace()
coral_integration = CoralMarketplaceIntegration(marketplace)

# -------------------
# Solana Wallet Helpers
# -------------------
# -------------------
# Solana Wallet Helpers
# -------------------

WALLET_FILE = "devnet-keypair.json"

def load_or_create_wallet():
    """Load or create a Solana devnet wallet"""
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            secret = json.load(f)
        return Keypair.from_secret_key(bytes(secret))
    kp = Keypair()
    with open(WALLET_FILE, "w") as f:
        json.dump(list(kp.secret_key), f)
    return kp

async def send_devnet_payment(sender: Keypair, recipient: str, sol_amount: float):
    """Send a real payment on Solana Devnet"""
    client = AsyncClient("https://api.devnet.solana.com")
    lamports = int(sol_amount * 1e9)  # SOL → lamports

    txn = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=sender.public_key,
                to_pubkey=Pubkey.from_string(recipient),
                lamports=lamports,
            )
        )
    )

    # Use TxOpts for reliable Devnet confirmation
    resp = await client.send_transaction(txn, sender, opts=TxOpts(skip_confirmation=False))
    await client.close()
    return resp

# -------------------
# WebSocket for Live Updates
# -------------------
connected_clients: List[WebSocket] = []

@app.websocket("/ws/updates")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        connected_clients.remove(ws)

async def broadcast_update(message: str):
    """Broadcast live updates to all connected WebSocket clients"""
    living_clients = []
    for client in connected_clients:
        try:
            await client.send_text(message)
            living_clients.append(client)
        except Exception:
            pass
    connected_clients[:] = living_clients

# -------------------
# Startup
# -------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Agent Marketplace with Coral Protocol...")
    await coral_integration.initialize_coral_integration()

# -------------------
# API Models
# -------------------
class PaymentRequest(BaseModel):
    agent_ids: List[str]
    user_wallet: str
    user_id: str = "demo_user"

class QuickWorkflowRequest(BaseModel):
    query: str
    selected_agents: List[str] = ["search", "content", "analysis"]
    user_wallet: str = "demo_wallet_123"
    budget_sol: float = 0.05

# -------------------
# UI
# -------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as f:
        return f.read()

# -------------------
# Marketplace Endpoints
# -------------------
@app.get("/api/agents")
async def get_available_agents():
    catalog = marketplace.get_agent_catalog()
    coral_status = coral_integration.get_coral_status()
    return {
        "agents": catalog["agents"],
        "total_agents": len(catalog["agents"]),
        "categories": catalog["categories"],
        "total_revenue_sol": catalog.get("total_revenue_sol", 0),
        "total_transactions": catalog.get("total_transactions", 0),
        "coral_protocol": coral_status
    }

@app.get("/api/marketplace/stats")
async def get_marketplace_stats():
    stats = marketplace.get_marketplace_stats()
    stats["coral_integration"] = coral_integration.get_coral_status()
    return stats

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    try:
        await broadcast_update(f"🚀 Workflow started: {request.query}")
        result = await coral_integration.execute_coral_workflow(
            query=request.query,
            selected_agents=request.selected_agents,
            user_wallet=request.user_wallet
        )
        await broadcast_update("✅ Workflow completed!")
        return result
    except Exception as e:
        await broadcast_update(f"❌ Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/create")
async def create_payment(request: PaymentRequest):
    try:
        # Each agent costs 0.01 SOL for demo
        total_cost = len(request.agent_ids) * 0.01

        kp = load_or_create_wallet()
        tx_sig = await send_devnet_payment(
            sender=kp,
            recipient=request.user_wallet,
            sol_amount=total_cost
        )

        await broadcast_update(f"💸 Payment sent: {tx_sig.value}")

        return {
            "status": "success",
            "total_cost_sol": total_cost,
            "transaction_signature": str(tx_sig.value),
            "explorer_url": f"https://explorer.solana.com/tx/{tx_sig.value}?cluster=devnet"
        }
    except Exception as e:
        await broadcast_update(f"❌ Payment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------
# Health + Quick Workflow
# -------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "marketplace": "running",
        "total_agents": len(marketplace.get_agent_catalog()["agents"]),
        "coral_protocol": coral_integration.get_coral_status(),
        "version": "2.0.0"
    }

@app.post("/api/demo/quick-workflow")
async def demo_quick_workflow(request: QuickWorkflowRequest):
    await broadcast_update(f"⚡ Quick workflow: {request.query}")
    result = await coral_integration.execute_coral_workflow(
        query=request.query,
        selected_agents=request.selected_agents,
        user_wallet=request.user_wallet
    )
    await broadcast_update("✅ Quick workflow done!")
    return result

# -------------------
# Entrypoint
# -------------------
if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("🌊 Agent Marketplace with Coral Protocol starting...")
    print("🏪 Available at: http://localhost:8000")
    print("🔌 Coral Server expected at: http://localhost:5555")
    print("🎯 Ready for hackathon demo with real Coral integration + WebSockets + Solana Devnet payments!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
