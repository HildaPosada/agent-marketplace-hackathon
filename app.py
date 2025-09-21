# app.py
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
    """Get all available agents in the marketplace"""
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
    """Get marketplace statistics"""
    return marketplace.get_marketplace_stats()

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    """Execute a multi-agent workflow with payments"""
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

@app.get("/api/workflow/{workflow_id}")
async def get_workflow_result(workflow_id: str):
    """Get workflow result by ID"""
    result = marketplace.get_workflow_result(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result

@app.get("/api/transactions")
async def get_recent_transactions():
    """Get recent marketplace transactions"""
    return marketplace.get_recent_transactions()

@app.post("/api/payment/create")
async def create_payment(request: PaymentRequest):
    """Create a payment request for selected agents"""
    try:
        payment_details = await marketplace.create_payment_request(
            agent_ids=request.agent_ids,
            user_wallet=request.user_wallet,
            user_id=request.user_id
        )
        return payment_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}/details")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    agent = marketplace.get_agent_details(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "marketplace": "running",
        "total_agents": len(marketplace.get_agent_catalog()["agents"]),
        "version": "1.0.0"
    }

# Demo endpoint for quick testing
@app.post("/api/demo/quick-workflow")
async def demo_quick_workflow(request: QuickWorkflowRequest):
    """Quick demo workflow for hackathon presentation"""
    workflow_request = WorkflowRequest(
        query=request.query,
        selected_agents=request.selected_agents,
        user_wallet=request.user_wallet,
        user_id="demo_user",
        preferences={"demo_mode": True}
    )
    
    return await execute_workflow(workflow_request)

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    print("🚀 Agent Marketplace starting...")
    print("🏪 Available at: http://localhost:8000")
    print("🎯 Ready for hackathon demo!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)