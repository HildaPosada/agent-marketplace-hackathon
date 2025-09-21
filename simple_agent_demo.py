# File 2: simple_agent_demo.py
# A working demo that doesn't require Coral Protocol setup

import asyncio
import json
from datetime import datetime
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class SimpleAgent:
    """Base agent class for our demo"""
    def __init__(self, name, capabilities):
        self.name = name
        self.capabilities = capabilities
        self.id = f"{name.lower()}_agent"
    
    def process(self, data):
        """Override in subclasses"""
        return data

class SearchAgent(SimpleAgent):
    def __init__(self):
        super().__init__("Search", ["web_search", "information_retrieval"])
    
    def process(self, query):
        # NEW: Log what was received
        print(f"📨 {self.name} Agent received: '{query}' (type: {type(query).__name__})")
        print(f"🔄 {self.name} Agent processing search request...")
        
        # Your existing code stays the same
        print(f"🔍 {self.name} Agent: Searching for '{query}'")
        time.sleep(1)  # Simulate processing time
        
        # Mock search results
        results = [
            {
                "title": f"Research Paper on {query}",
                "snippet": f"This comprehensive study examines {query} from multiple perspectives, providing insights into current trends and future implications.",
                "url": f"https://research.example.com/{query.replace(' ', '-')}"
            },
            {
                "title": f"{query}: Industry Analysis", 
                "snippet": f"Industry experts analyze the impact of {query} on various sectors, highlighting key opportunities and challenges.",
                "url": f"https://industry.example.com/{query.replace(' ', '-')}"
            },
            {
                "title": f"Latest Developments in {query}",
                "snippet": f"Breaking news and recent developments related to {query}, including expert opinions and market reactions.",
                "url": f"https://news.example.com/{query.replace(' ', '-')}"
            }
        ]
        
        result = {
            "agent": self.name,
            "task": "search_completed",
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        # NEW: Log what's being sent to next agent
        print(f"📤 {self.name} Agent sending {len(results)} results to Summarizer Agent")
        print(f"🔗 Agent communication: Search → Summarizer")
        
        return result

class SummarizerAgent(SimpleAgent):
    def __init__(self):
        super().__init__("Summarizer", ["text_analysis", "content_summarization"])
    
    def process(self, search_data):
        # NEW: Log what was received
        print(f"📨 {self.name} Agent received: Search data with {len(search_data.get('results', []))} sources")
        print(f"🔄 {self.name} Agent processing summarization...")
        
        # Your existing code stays the same
        print(f"📝 {self.name} Agent: Summarizing search results")
        time.sleep(1.5)  # Simulate processing
        
        query = search_data["query"]
        results = search_data["results"]
        
        # Create summary
        summary = f"Research Summary for '{query}':\n\n"
        summary += f"Based on analysis of {len(results)} sources:\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}: {result['snippet'][:100]}...\n\n"
        
        summary += f"Key Insights:\n"
        summary += f"• Multiple perspectives available on {query}\n"
        summary += f"• Current research shows significant interest in this topic\n"
        summary += f"• Industry impact appears to be substantial\n\n"
        summary += f"Summary generated at: {datetime.now().strftime('%H:%M:%S')}"
        
        result = {
            "agent": self.name,
            "task": "summary_completed", 
            "original_query": query,
            "summary": summary,
            "source_count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
        # NEW: Log what's being sent to next agent
        print(f"📤 {self.name} Agent sending summary ({len(summary)} chars) to Validator Agent")
        print(f"🔗 Agent communication: Summarizer → Validator")
        
        return result

class ValidatorAgent(SimpleAgent):
    def __init__(self):
        super().__init__("Validator", ["fact_checking", "quality_assessment"])
    
    def process(self, summary_data):
        # NEW: Log what was received
        print(f"📨 {self.name} Agent received: Summary data from Summarizer Agent")
        print(f"🔄 {self.name} Agent processing validation...")
        
        # Your existing code stays the same
        print(f"✅ {self.name} Agent: Validating information quality")
        time.sleep(1)  # Simulate validation
        
        summary = summary_data["summary"]
        source_count = summary_data["source_count"]
        
        # Calculate confidence score
        confidence = min(95, 60 + (source_count * 10))
        
        validated_summary = summary + f"\n\n🔍 VALIDATION REPORT:\n"
        validated_summary += f"• Sources analyzed: {source_count}\n"
        validated_summary += f"• Confidence score: {confidence}%\n"
        validated_summary += f"• Information quality: {'High' if confidence > 80 else 'Medium'}\n"
        validated_summary += f"• Validation completed: {datetime.now().strftime('%H:%M:%S')}\n"
        
        result = {
            "agent": self.name,
            "task": "validation_completed",
            "final_summary": validated_summary,
            "confidence_score": confidence,
            "quality_rating": "High" if confidence > 80 else "Medium",
            "timestamp": datetime.now().isoformat()
        }
        
        # NEW: Log final output
        print(f"📤 {self.name} Agent completed validation with {confidence}% confidence")
        print(f"🏁 Agent workflow complete: Search → Summarizer → Validator ✅")
        
        return result

class AgentOrchestrator:
    """Coordinates the multi-agent workflow"""
    
    def __init__(self):
        self.search_agent = SearchAgent()
        self.summarizer_agent = SummarizerAgent() 
        self.validator_agent = ValidatorAgent()
        self.results_history = []
    
    async def process_query(self, query):
        """Run the full multi-agent pipeline"""
        print(f"\n🚀 STARTING MULTI-AGENT RESEARCH PIPELINE")
        print(f"📋 Query: '{query}'")
        print(f"👥 Agents: {self.search_agent.name} → {self.summarizer_agent.name} → {self.validator_agent.name}")
        print("-" * 60)
        
        # Step 1: Search
        search_result = self.search_agent.process(query)
        print(f"   ✓ Step 1 completed - {self.search_agent.name} Agent")
        
        # Step 2: Summarize
        summary_result = self.summarizer_agent.process(search_result)
        print(f"   ✓ Step 2 completed - {self.summarizer_agent.name} Agent")
        
        # Step 3: Validate
        final_result = self.validator_agent.process(summary_result)
        print(f"   ✓ Step 3 completed - {self.validator_agent.name} Agent")
        
        print("-" * 60)
        print(f"🎉 MULTI-AGENT RESEARCH COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total pipeline time: ~3.5 seconds")
        print(f"🤖 All 3 agents collaborated successfully")
        print()
        
        # Store result
        complete_result = {
            "query": query,
            "search_phase": search_result,
            "summary_phase": summary_result, 
            "validation_phase": final_result,
            "agents_used": ["Search", "Summarizer", "Validator"],
            "total_processing_time": "3.5 seconds",
            "completed_at": datetime.now().isoformat()
        }
        
        self.results_history.append(complete_result)
        
        return complete_result

# Simple web interface
class DemoWebHandler(BaseHTTPRequestHandler):
    orchestrator = AgentOrchestrator()
    
    def do_GET(self):
        if self.path == '/':
            self.send_html_response()
        elif self.path == '/api/results':
            self.send_json_response({"results": self.orchestrator.results_history})
        elif self.path == '/health':
            self.send_json_response({"status": "running", "agents": 3})
    
    def do_POST(self):
        if self.path == '/api/research':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                query = data.get('query', '').strip()
                
                if not query:
                    self.send_json_response({"error": "Query required"}, 400)
                    return
                
                # Run research in background
                def run_research():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.orchestrator.process_query(query))
                
                thread = threading.Thread(target=run_research)
                thread.daemon = True
                thread.start()
                
                self.send_json_response({"status": "started", "query": query})
                
            except json.JSONDecodeError:
                self.send_json_response({"error": "Invalid JSON"}, 400)
    
    def send_html_response(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Internet of Agents - Multi-Agent Research Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .agent-card {
            background: white;
            border: 2px solid #e1e5e9;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .agent-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .agent-icon { font-size: 2.5em; margin-bottom: 10px; }
        .agent-name { font-size: 1.3em; font-weight: bold; color: #333; margin-bottom: 10px; }
        .agent-desc { color: #666; font-size: 0.9em; }
        .search-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .search-form {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        #queryInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        #queryInput:focus { border-color: #667eea; }
        #searchBtn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        #searchBtn:hover { transform: scale(1.05); }
        #searchBtn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none; 
        }
        .status {
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-weight: bold;
        }
        .status.processing { background: #fff3cd; color: #856404; }
        .status.completed { background: #d4edda; color: #155724; }
        .results-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #e1e5e9;
        }
        .result-item {
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fdfdfd;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e9ecef;
        }
        .result-query {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        .result-time {
            color: #666;
            font-size: 0.9em;
        }
        .agent-flow {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .flow-step {
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .result-summary {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            white-space: pre-wrap;
            font-family: Georgia, serif;
            line-height: 1.6;
        }
        .loading {
            display: inline-block;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .demo-examples {
            margin-top: 15px;
            font-size: 0.9em;
            color: #666;
        }
        .example-queries {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        .example-query {
            background: #e9ecef;
            padding: 5px 12px;
            border-radius: 15px;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        .example-query:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Internet of Agents</h1>
        <p class="subtitle">Multi-Agent Research Assistant Demo</p>
        
        <div class="agents-grid">
            <div class="agent-card">
                <div class="agent-icon">🔍</div>
                <div class="agent-name">Search Agent</div>
                <div class="agent-desc">Finds and retrieves relevant information from multiple sources</div>
            </div>
            <div class="agent-card">
                <div class="agent-icon">📝</div>
                <div class="agent-name">Summarizer Agent</div>
                <div class="agent-desc">Creates comprehensive summaries and extracts key insights</div>
            </div>
            <div class="agent-card">
                <div class="agent-icon">✅</div>
                <div class="agent-name">Validator Agent</div>
                <div class="agent-desc">Validates information quality and provides confidence scores</div>
            </div>
        </div>
        
        <div class="search-section">
            <h3 style="margin-bottom: 15px; color: #333;">Start Your Research</h3>
            <div class="search-form">
                <input type="text" id="queryInput" placeholder="Enter your research question (e.g., artificial intelligence, climate change, blockchain technology...)" />
                <button id="searchBtn" onclick="startResearch()">Research</button>
            </div>
            <div class="demo-examples">
                <strong>Try these examples:</strong>
                <div class="example-queries">
                    <span class="example-query" onclick="setQuery('artificial intelligence')">Artificial Intelligence</span>
                    <span class="example-query" onclick="setQuery('climate change solutions')">Climate Solutions</span>
                    <span class="example-query" onclick="setQuery('renewable energy trends')">Renewable Energy</span>
                    <span class="example-query" onclick="setQuery('space exploration')">Space Exploration</span>
                </div>
            </div>
            <div id="status"></div>
        </div>
        
        <div class="results-section">
            <h3 style="margin-bottom: 20px; color: #333;">Research Results</h3>
            <div id="results">
                <p style="color: #666; text-align: center; padding: 40px;">
                    Enter a research query above to see the multi-agent system in action!
                </p>
            </div>
        </div>
    </div>

    <script>
        let currentResultCount = 0;
        let currentQuery = '';
        
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        async function startResearch() {
            const query = document.getElementById('queryInput').value.trim();
            if (!query) {
                alert('Please enter a research question');
                return;
            }
            
            currentQuery = query;
            
            const btn = document.getElementById('searchBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="loading">⟳</span> Researching...';
            
            status.className = 'status processing';
            status.innerHTML = '🚀 Multi-agent research started...';
            
            try {
                const response = await fetch('/api/research', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                
                if (response.ok) {
                    status.innerHTML = '🔍 Agents are collaborating on your research...';
                    // Get current result count BEFORE starting to poll
                    const initialResponse = await fetch('/api/results');
                    const initialData = await initialResponse.json();
                    currentResultCount = initialData.results ? initialData.results.length : 0;
                    
                    // Start polling for NEW results
                    pollResults();
                } else {
                    throw new Error('Research failed');
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = '❌ Research failed. Please try again.';
                btn.disabled = false;
                btn.innerHTML = 'Research';
            }
        }
        
        async function pollResults() {
            try {
                const response = await fetch('/api/results');
                const data = await response.json();
                
                // Check if we have NEW results (more than we had before)
                if (data.results && data.results.length > currentResultCount) {
                    displayResults(data.results);
                    currentResultCount = data.results.length;
                    document.getElementById('status').className = 'status completed';
                    document.getElementById('status').innerHTML = '✅ Research completed!';
                    document.getElementById('searchBtn').disabled = false;
                    document.getElementById('searchBtn').innerHTML = 'Research';
                } else {
                    // Keep polling every 500ms until we get a new result
                    setTimeout(pollResults, 500);
                }
            } catch (error) {
                setTimeout(pollResults, 500);
            }
        }
        
        function displayResults(results) {
            const resultsDiv = document.getElementById('results');
            
            resultsDiv.innerHTML = results.slice(-3).reverse().map(result => `
                <div class="result-item">
                    <div class="result-header">
                        <div class="result-query">${result.query}</div>
                        <div class="result-time">${new Date(result.completed_at).toLocaleString()}</div>
                    </div>
                    <div class="agent-flow">
                        <div class="flow-step">🔍 Search</div>
                        <div class="flow-step">📝 Summarize</div>
                        <div class="flow-step">✅ Validate</div>
                    </div>
                    <div class="result-summary">${result.validation_phase.final_summary}</div>
                </div>
            `).join('');
        }
        
        // Allow Enter key to start research
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startResearch();
            }
        });
        
        // Load any existing results on page load
        window.addEventListener('load', function() {
            fetch('/api/results')
                .then(r => r.json())
                .then(data => {
                    if (data.results && data.results.length > 0) {
                        displayResults(data.results);
                    }
                })
                .catch(() => {});
        });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def start_server():
    server = HTTPServer(('0.0.0.0', 8000), DemoWebHandler)
    print("\n🚀 Internet of Agents Demo Server Starting...")
    print("📍 Server running on http://localhost:8000")
    print("🔗 Codespaces will auto-forward this port for demo access")
    print("🤖 3 agents ready: Search, Summarizer, Validator")
    print("\n✨ Ready for hackathon demo!\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_server()