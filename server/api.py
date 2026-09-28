import ollama
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="AI Tool Evaluator API")

# Configure CORS to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1. Request Payload Schema (from Next.js to FastAPI)
class ToolRequest(BaseModel):
    tool_name: str


# 2. Response Payload Schema (from FastAPI to Next.js)
class TechStackReview(BaseModel):
    tool_name: str = Field(description="Name of the software tool")
    pros: list[str] = Field(description="Top 3 pros of this tool")
    cons: list[str] = Field(description="Top 3 cons of this tool")
    rating_out_of_10: float = Field(description="Score from 1 to 10")


# 3. REST Endpoint Definition
@app.post("/api/evaluate", response_model=TechStackReview)
async def evaluate_tool(payload: ToolRequest):
    try:
        response = ollama.chat(
            model="qwen2.5-coder:7b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a tech evaluator. Respond only with the requested JSON schema.",
                },
                {
                    "role": "user",
                    "content": f"Evaluate the tool '{payload.tool_name}' for a web developer.",
                },
            ],
            format=TechStackReview.model_json_schema(),
        )

        # Parse and validate the response against our Pydantic model
        structured_data = TechStackReview.model_validate_json(
            response["message"]["content"]
        )
        return structured_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
