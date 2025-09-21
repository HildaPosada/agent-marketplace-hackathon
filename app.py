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

# Import our enhanced marketplace with Coral integration
from agent_marketplace import AgentMarketplace, WorkflowRequest
from coral_integration import CoralMarketplaceIntegration

app = FastAPI(
    title="🏪 Agent Marketplace - Coral Protocol Integration",
    description="Rent specialized AI agents with Solana payments powered by Coral Protocol",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the marketplace with Coral integration
marketplace = AgentMarketplace()
coral_integration = CoralMarketplaceIntegration(marketplace)

# Initialize Coral Protocol on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Coral Protocol integration on startup"""
    print("🚀 Starting Agent Marketplace with Coral Protocol...")
    await coral_integration.initialize_coral_integration()

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

# -------------------
# Marketplace Endpoints
# -------------------

@app.get("/api/agents")
async def get_available_agents():
    """Get all available agents in the marketplace with Coral status"""
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
    """Get marketplace statistics with Coral integration status"""
    stats = marketplace.get_marketplace_stats()
    coral_status = coral_integration.get_coral_status()
    
    stats["coral_integration"] = coral_status
    return stats

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest):
    """Execute a multi-agent workflow with Coral Protocol coordination"""
    try:
        result = await coral_integration.execute_coral_workflow(
            query=request.query,
            selected_agents=request.selected_agents,
            user_wallet=request.user_wallet
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

# -------------------
# Coral Protocol Endpoints
# -------------------

@app.get("/api/coral/status")
async def get_coral_status():
    """Get Coral Protocol integration status"""
    return coral_integration.get_coral_status()

@app.post("/api/coral/discover-agents")
async def coral_discover_agents(request: Dict[str, Any]):
    """Coral Protocol tool endpoint for agent discovery"""
    category = request.get("category", "All")
    max_price = request.get("max_price_sol")
    
    agents = marketplace.get_agent_catalog()["agents"]
    
    if category != "All":
        agents = [a for a in agents if a["category"] == category]
    if max_price:
        agents = [a for a in agents if a["price_sol"] <= max_price]
    
    return {
        "discovered_agents": len(agents),
        "agents": agents,
        "coral_protocol_enabled": True
    }

@app.post("/api/coral/execute-workflow")
async def coral_execute_workflow(request: Dict[str, Any]):
    """Coral Protocol tool endpoint for workflow execution"""
    query = request.get("query")
    agent_ids = request.get("agent_ids", [])
    user_wallet = request.get("user_wallet", "coral_demo_wallet")
    
    if not query or not agent_ids:
        raise HTTPException(status_code=400, detail="Query and agent_ids required")
    
    result = await coral_integration.execute_coral_workflow(query, agent_ids, user_wallet)
    
    return {
        "workflow_executed": True,
        "coral_coordinated": True,
        "result": result
    }

# Debug GET endpoint for quick testing
@app.get("/api/agents/discover")
async def debug_discover_agents():
    """Debug endpoint: see all agents directly"""
    return marketplace.get_agent_catalog()

@app.get("/health")
async def health_check():
    """Health check endpoint with Coral status"""
    coral_status = coral_integration.get_coral_status()
    
    return {
        "status": "healthy",
        "marketplace": "running",
        "total_agents": len(marketplace.get_agent_catalog()["agents"]),
        "coral_protocol": coral_status,
        "version": "2.0.0"
    }

@app.post("/api/demo/quick-workflow")
async def demo_quick_workflow(request: QuickWorkflowRequest):
    """Quick demo workflow for hackathon presentation with Coral integration"""
    result = await coral_integration.execute_coral_workflow(
        query=request.query,
        selected_agents=request.selected_agents,
        user_wallet=request.user_wallet
    )
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
    print("🎯 Ready for hackathon demo with real Coral integration!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
