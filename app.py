from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
import os

# Import our agent marketplace
from agent_marketplace import AgentMarketplace, WorkflowRequest

app = FastAPI(
    title="🏪 Agent Marketplace - Internet of Agents",
    description="Rent specialized AI agents with Solana payments powered by Coral Protocol",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the marketplace
marketplace = AgentMarketplace()

# API Models
class PaymentRequest(BaseModel):
    agent_ids: List[str]
    user_wallet: str
    user_id: str = "demo_user"

class QuickWorkflowRequest(BaseModel):
    query: str
    selected_agents: List[str] = ["search", "content", "analysis"]
    user_wallet: str = "demo_wallet_123"
    budget_sol: float = 0.05

# Serve the stunning UI
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as f:
        return f.read()

# API Endpoints
@app.get("/api/agents")
async def get_available_agents():
    catalog = marketplace.get_agent_catalog()
    return {
        "agents": catalog["agents"],
        "total_agents": len(catalog["agents"]),
        "categories": catalog["categories"],
        "total_revenue_sol": catalog.get("total_revenue_sol", 0),
        "total_transactions": catalog.get("total_transactions", 0)
    }

@app.get("/api/marketplace/stats")
async def get_marketplace_stats():
    return marketplace.get_marketplace_stats()

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    try:
        result = await marketplace.execute_paid_workflow(
            query=request.query,
            selected_agents=request.selected_agents,
            user_wallet=request.user_wallet,
            user_id=request.user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "marketplace": "running",
        "total_agents": len(marketplace.get_agent_catalog()["agents"]),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("🚀 Agent Marketplace starting...")
    print("🏪 Available at: http://localhost:8000")
    print("🎯 Ready for hackathon demo!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
