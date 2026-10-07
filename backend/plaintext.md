
```
C:\FREE\shadow-raiders\backend
│   screener_batch.py
│   .env
└───app
    │   main.py
    │   __init__.py
    ├───core
    │       security.py
    │       __init__.py
    └───routers
            market.py
            radar.py
            __init__.py
```

# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 서버 실행
python -m uvicorn app.main:app --reload --port 8000

# 로컬 서버 확인
http://127.0.0.1:8000/

# 로컬 swagger
http://127.0.0.1:8000/docs#