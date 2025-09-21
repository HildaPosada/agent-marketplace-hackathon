import asyncio
import json
import uuid
import yaml
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel

class WorkflowRequest(BaseModel):
    query: str
    selected_agents: List[str] = ["search", "content", "analysis"]
    user_wallet: str = "demo_wallet"
    user_id: str = "demo_user"
    preferences: Dict = {}

@dataclass
class Agent:
    id: str
    name: str
    description: str
    price_sol: float
    price_usd: float
    capabilities: List[str]
    category: str
    owner: str
    rating: float
    total_uses: int
    avg_processing_time: float
    success_rate: float
    icon: str

class AgentMarketplace:
    def __init__(self):
        self.agents = []

        # Load agents dynamically from YAML files
        agents_path = "agents"
        if os.path.exists(agents_path):
            for file in os.listdir(agents_path):
                if file.endswith(".yaml"):
                    with open(os.path.join(agents_path, file), "r") as f:
                        data = yaml.safe_load(f)
                        self.agents.append(Agent(**data))
        else:
            print("⚠️ Agents folder not found. No agents loaded.")

        self.workflows = {}
        self.transactions = []
        
    def get_agent_catalog(self):
        return {
            "agents": [asdict(agent) for agent in self.agents],
            "categories": list(set(agent.category for agent in self.agents)),
            "total_revenue_sol": sum(tx.get("amount_sol", 0) for tx in self.transactions),
            "total_transactions": len(self.transactions)
        }
    
    async def execute_paid_workflow(self, query: str, selected_agents: List[str], user_wallet: str, user_id: str):
        workflow_id = str(uuid.uuid4())
        
        print(f"🚀 Executing workflow: {query}")
        print(f"🤖 Selected agents: {selected_agents}")
        
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Calculate costs
        total_cost_sol = 0
        agent_results = {}
        
        for agent_id in selected_agents:
            agent = next((a for a in self.agents if a.id == agent_id), None)
            if agent:
                total_cost_sol += agent.price_sol
                
                # Simulate agent processing
                if agent_id == "search":
                    agent_results["search"] = {
                        "results": {
                            "web_results": [
                                {
                                    "title": f"Market Analysis: {query}",
                                    "snippet": f"Comprehensive analysis of {query} market trends"
                                }
                            ],
                            "market_intelligence": {
                                "market_size_usd": "$47.2B",
                                "growth_rate": "23.4% CAGR"
                            }
                        },
                        "confidence_score": 0.94
                    }
                elif agent_id == "content":
                    agent_results["content"] = {
                        "content": {
                            "blog_post": {"word_count": 1250, "seo_score": 89}
                        }
                    }
                elif agent_id == "analysis":
                    agent_results["analysis"] = {
                        "analysis": {
                            "executive_summary": f"Strategic analysis reveals significant market opportunity in {query}",
                            "investment_thesis": {
                                "investment_required": "$1.5M - $3M",
                                "expected_roi": "300-500% over 3 years"
                            }
                        }
                    }
        
        # Create transaction
        transaction = {
            "id": str(uuid.uuid4()),
            "amount_sol": total_cost_sol,
            "user_wallet": user_wallet,
            "timestamp": datetime.now().isoformat()
        }
        self.transactions.append(transaction)
        
        workflow = {
            "id": workflow_id,
            "query": query,
            "selected_agents": selected_agents,
            "total_cost_sol": total_cost_sol,
            "total_cost_usd": total_cost_sol * 180,
            "results": agent_results,
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        
        self.workflows[workflow_id] = workflow
        
        print(f"✅ Workflow completed! Cost: {total_cost_sol:.3f} SOL")
        return workflow
    
    def get_marketplace_stats(self):
        total_revenue = sum(tx.get("amount_sol", 0) for tx in self.transactions)
        return {
            "total_agents": len(self.agents),
            "total_workflows": len(self.workflows),
            "total_revenue_sol": total_revenue,
            "total_revenue_usd": total_revenue * 180
        }


if __name__ == "__main__":
    mp = AgentMarketplace()
    print("Loaded agents:", [a.id for a in mp.agents])

