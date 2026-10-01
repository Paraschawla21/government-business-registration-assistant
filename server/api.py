import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent import run_business_setup_agent
from schemas import BusinessProfile, BusinessSetupReport

app = FastAPI(title="AI Tool Evaluator API")

MAX_CONTENT_LENGTH = int(os.getenv("MAX_REQUEST_BYTES", "65536"))

# Configure CORS to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/evaluate", response_model=BusinessSetupReport)
async def evaluate_business_profile(payload: BusinessProfile):
    try:
        if len(payload.model_dump_json().encode("utf-8")) > MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=413,
                detail="Request payload too large.",
            )
        return run_business_setup_agent(payload)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
