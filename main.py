import hmac
from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

EMAIL = "25ds3000071@ds.study.iitm.ac.in"
API_KEY = "ak_fzd6yrp8k1nco3phy9rbtaxn"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analytics")
async def analytics(request: Request, x_api_key: str | None = Header(default=None)):
    if x_api_key is None or not hmac.compare_digest(x_api_key.encode(), API_KEY.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    try:
        body = await request.json()
        events = body["events"]
        assert isinstance(events, list)
    except Exception:
        raise HTTPException(status_code=400, detail="body must be {\"events\": [...]}")

    users = set()
    per_user = defaultdict(float)
    revenue = 0.0
    for e in events:
        u = e.get("user")
        users.add(u)
        amt = float(e.get("amount", 0) or 0)
        if amt > 0:
            revenue += amt
            per_user[u] += amt
    top = max(per_user, key=per_user.get) if per_user else None
    return {"email": EMAIL, "total_events": len(events), "unique_users": len(users),
            "revenue": round(revenue, 2), "top_user": top}

@app.get("/")
async def root():
    return {"ok": True}
