from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from simple_agent_demo import AgentOrchestrator

app = FastAPI()
orchestrator = AgentOrchestrator()

# Full HTML UI from DemoWebHandler + favicon fix
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Internet of Agents - Multi-Agent Research Demo</title>
    <link rel="icon" href="data:;base64,iVBORw0KGgo=">
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
        #searchBtn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
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
        .result-time { color: #666; font-size: 0.9em; }
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
        .loading { display: inline-block; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .demo-examples { margin-top: 15px; font-size: 0.9em; color: #666; }
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
        .example-query:hover { background: #667eea; color: white; }
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
                <input type="text" id="queryInput" placeholder="Enter your research question..." />
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
                    const initialResponse = await fetch('/api/results');
                    const initialData = await initialResponse.json();
                    currentResultCount = initialData.results ? initialData.results.length : 0;
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
                
                if (data.results && data.results.length > currentResultCount) {
                    displayResults(data.results);
                    currentResultCount = data.results.length;
                    document.getElementById('status').className = 'status completed';
                    document.getElementById('status').innerHTML = '✅ Research completed!';
                    document.getElementById('searchBtn').disabled = false;
                    document.getElementById('searchBtn').innerHTML = 'Research';
                } else {
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
        
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') startResearch();
        });
        
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
</html>"""

@app.get("/")
async def home():
    return HTMLResponse(HTML_PAGE)

@app.get("/health")
async def health():
    return {"status": "running", "agents": 3}

@app.get("/api/results")
async def get_results():
    return {"results": orchestrator.results_history}

@app.post("/api/research")
async def research(request: Request):
    body = await request.json()
    query = body.get("query", "").strip()
    if not query:
        return JSONResponse({"error": "Query required"}, status_code=400)
    result = await orchestrator.process_query(query)
    return result
