from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market, radar, closing_bet

app = FastAPI(title="Shadow Raiders API", version="1.0.0")

# CORS 허용 출처 명시
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:4444",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4444",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(radar.router)
app.include_router(closing_bet.router)

@app.get("/")
def root():
    return {"message": "Shadow Raiders Service is running"}