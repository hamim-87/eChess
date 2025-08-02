from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

class MoveModel(BaseModel):
    move: str

latest_move = ""

@app.post("/update-move")
async def update_move(data: MoveModel):
    global latest_move
    latest_move = data.move
    print("✅ Move received:", latest_move)
    return {"status": "success"}

@app.get("/get-move")
async def get_move():
    return {"move": latest_move}
