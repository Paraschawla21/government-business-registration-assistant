import ollama
from pydantic import BaseModel, Field


# 1. Define the exact JSON schema you want back
class TechStackReview(BaseModel):
    tool_name: str = Field(description="Name of the software tool")
    pros: list[str] = Field(description="Top 3 pros of this tool")
    cons: list[str] = Field(description="Top 3 cons of this tool")
    rating_out_of_10: float = Field(description="Score from 1 to 10")


def evaluate_tool(tool: str) -> TechStackReview:
    print(f"Evaluating '{tool}' with structured output...\n")

    # 2. Pass the Pydantic schema to Ollama format parameter
    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=[
            {
                "role": "system",
                "content": "You are a tech evaluator. Respond only with the requested JSON schema.",
            },
            {
                "role": "user",
                "content": f"Evaluate the tool '{tool}' for a web developer.",
            },
        ],
        format=TechStackReview.model_json_schema(),  # Enforces JSON schema
    )

    # 3. Parse the JSON string directly into a typed Python object
    structured_data = TechStackReview.model_validate_json(
        response["message"]["content"]
    )
    return structured_data


if __name__ == "__main__":
    result = evaluate_tool("Next.js")

    # Now you can access properties safely just like a TypeScript object!
    print(f"Tool: {result.tool_name}")
    print(f"Rating: {result.rating_out_of_10}/10")
    print(f"Pros: {result.pros}")
    print(f"Cons: {result.cons}")
