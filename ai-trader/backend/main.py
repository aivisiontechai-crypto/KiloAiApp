"""
AI Trader - FastAPI Server
"""
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import os

# Import our trading system
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trading_system import trading_system

app = FastAPI(title="AI Trader - Agent Swarm Trading System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
async def get_dashboard():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))

@app.get("/api/analysis")
async def get_analysis():
    result = await trading_system.run_analysis()
    return result

@app.get("/api/portfolio")
async def get_portfolio():
    from trading_system import MarketDataService
    md = MarketDataService()
    market_data = md.get_market_data()
    current_prices = {d.symbol: d.price for d in market_data}
    portfolio = trading_system.portfolio.get_portfolio_value(current_prices)
    return {
        "portfolio": trading_system._portfolio_to_dict(portfolio),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/history")
async def get_history():
    history = trading_system.get_performance_history()
    return {"history": history, "timestamp": datetime.now().isoformat()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            result = await trading_system.run_analysis()
            await websocket.send_json(result)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass

class ConnectionManager:
    def __init__(self):
        self.active_connections: list = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("=" * 60)
    print("  AI TRADER - AGENT SWARM SYSTEM")
    print("  Dashboard: http://localhost:8000")
    print("  API Docs:  http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
