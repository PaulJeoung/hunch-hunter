import os
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market, radar, closing_bet

ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()
is_production = ENVIRONMENT == "production"

app = FastAPI(
    title="Hunch Hunter API",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json"
)

origins = [
    "http://localhost:4449",
    "http://127.0.0.1:4449",
    "https://hunch-hunter-web.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(radar.router)
app.include_router(closing_bet.router)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "SERVICE AVAILABLE",
        "meta": {
            "codename": "HH",
            "timestamp": 1791468932,
            "uptime_seconds": 18273645,
            "security_level": "DELTA"
        },
        "message": "SYSTEM HEALTH OPTIMAL // NO INTRUSIONS DETECTED // ZERO ANOMALIES",
        "vitals": {
            "heartbeat": "STABLE",
            "core_load": "0.14",
            "memory_leak_risk": "0.00%"
        },
        "clusters": {
            "auth_matrix": "GREEN",
            "shadow_db": "SYNCHRONIZED",
            "quantum_firewall": "ENFORCED"
        }
    }

@app.get("/")
def root():
    return {"message": "Hunch Hunter Service is running"}