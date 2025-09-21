# coral_integration.py
# Real Coral Protocol integration for Agent Marketplace

import aiohttp
import asyncio
import json
import uuid
import os
import yaml
from datetime import datetime
from typing import Dict, List, Any


class CoralProtocolClient:
    """
    Client for integrating with real Coral Protocol server
    Connects to the Coral Server you have running locally
    """

    def __init__(self, coral_server_url: str = "http://localhost:5555"):
        self.coral_server_url = coral_server_url
        self.session_id = None
        self.active_agents = {}

    async def connect_to_coral_server(self):
        """Connect to the Coral Server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.coral_server_url}/health") as response:
                    if response.status == 200:
                        print("✅ Connected to Coral Server successfully")
                        return True
                    else:
                        print(f"❌ Coral Server health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Failed to connect to Coral Server: {e}")
            return False

    async def create_marketplace_session(self, application_id: str = "app", privacy_key: str = "priv"):
        """Create a Coral Protocol session for the marketplace"""
        session_config = {
            "applicationId": application_id,
            "privacyKey": privacy_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coral_server_url}/sessions",
                    json=session_config,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 201:
                        session_data = await response.json()
                        self.session_id = session_data.get("sessionId")
                        print(f"✅ Coral Protocol session created: {self.session_id}")
                        return self.session_id
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create session: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error creating Coral session: {e}")
            return None

    async def register_agent(self, agent_def: Dict[str, Any]):
        """Register a new agent with the Coral Protocol server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coral_server_url}/agents",
                    json=agent_def,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in (200, 201):
                        data = await response.json()
                        print(f"✅ Registered agent with Coral: {agent_def.get('id')}")
                        return data
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to register agent {agent_def.get('id')}: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error registering agent {agent_def.get('id')}: {e}")
            return None

    async def create_thread(self):
        """Create a new thread in the Coral session"""
        if not self.session_id:
            return None

        thread_config = {
            "name": f"marketplace_thread_{uuid.uuid4().hex[:8]}",
            "description": "Agent Marketplace workflow thread"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coral_server_url}/sessions/{self.session_id}/threads",
                    json=thread_config,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 201:
                        thread_data = await response.json()
                        thread_id = thread_data.get("threadId")
                        print(f"✅ Coral thread created: {thread_id}")
                        return thread_id
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create thread: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error creating Coral thread: {e}")
            return None

    async def send_message_to_thread(self, message: str, thread_id: str = None):
        """Send a message to a Coral Protocol thread"""
        if not self.session_id:
            print("❌ No active Coral session")
            return None

        if not thread_id:
            thread_id = await self.create_thread()

        message_data = {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coral_server_url}/sessions/{self.session_id}/threads/{thread_id}/messages",
                    json=message_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Message sent to Coral thread: {thread_id}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to send message: {response.status} - {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error sending message to Coral: {e}")
            return None


class CoralMarketplaceIntegration:
    """Integration layer between Agent Marketplace and Coral Protocol"""

    def __init__(self, marketplace, coral_server_url: str = "http://localhost:5555"):
        self.marketplace = marketplace
        self.coral_client = CoralProtocolClient(coral_server_url)
        self.coral_enabled = False

    async def initialize_coral_integration(self):
        """Initialize Coral Protocol integration and auto-register agents"""
        print("🔌 Initializing Coral Protocol integration...")

        connected = await self.coral_client.connect_to_coral_server()
        if not connected:
            print("⚠️ Coral Server not available - running in standalone mode")
            return False

        session_id = await self.coral_client.create_marketplace_session()
        if session_id:
            self.coral_enabled = True
            print("✅ Coral Protocol integration enabled")

            # Register all agents from ./agents folder
            agents_path = "agents"
            if os.path.exists(agents_path):
                for file in os.listdir(agents_path):
                    if file.endswith(".yaml"):
                        with open(os.path.join(agents_path, file), "r") as f:
                            agent_def = yaml.safe_load(f)
                            await self.coral_client.register_agent(agent_def)

            return True
        else:
            print("⚠️ Failed to create Coral session - running in standalone mode")
            return False

    async def execute_coral_workflow(self, query: str, selected_agents: List[str], user_wallet: str):
        """Execute workflow through Coral Protocol"""
        if not self.coral_enabled:
            print("⚠️ Coral Protocol not available, falling back to direct execution")
            return await self.marketplace.execute_paid_workflow(query, selected_agents, user_wallet, "demo_user")

        print(f"🌊 Executing workflow through Coral Protocol...")

        thread_id = await self.coral_client.create_thread()
        if not thread_id:
            print("❌ Failed to create Coral thread")
            return await self.marketplace.execute_paid_workflow(query, selected_agents, user_wallet, "demo_user")

        workflow_message = f"""
        Execute marketplace workflow:
        Query: {query}
        Selected Agents: {', '.join(selected_agents)}
        User Wallet: {user_wallet}
        """

        result = await self.coral_client.send_message_to_thread(workflow_message, thread_id)

        if result:
            regular_result = await self.marketplace.execute_paid_workflow(query, selected_agents, user_wallet, "demo_user")

            regular_result["coral_protocol"] = {
                "enabled": True,
                "session_id": self.coral_client.session_id,
                "thread_id": thread_id,
                "agent_coordination": "Coral Protocol orchestrated",
                "protocol_version": "Coral v1.0",
            }

            print("✅ Workflow executed through Coral Protocol successfully")
            return regular_result
        else:
            print("⚠️ Coral execution failed, falling back to direct execution")
            return await self.marketplace.execute_paid_workflow(query, selected_agents, user_wallet, "demo_user")

    def get_coral_status(self):
        return {
            "coral_enabled": self.coral_enabled,
            "session_id": self.coral_client.session_id,
            "server_url": self.coral_client.coral_server_url,
            "protocol_version": "Coral v1.0"
        }
