from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market, radar, closing_bet

app = FastAPI(title="Hunch Hunter API", version="1.0.0")

# CORS 허용 목록
origins = [
    "http://localhost:5173",
    "http://localhost:4444",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "https://hunch-hunter-web.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com", # Render 서브도메인 전체 포괄 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(radar.router)
app.include_router(closing_bet.router)

@app.get("/")
def root():
    return {"message": "Hunch Hunter API is running"}