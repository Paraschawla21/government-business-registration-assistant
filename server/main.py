import ollama


def ask_local_llm(user_prompt: str) -> str:
    print(f"Sending prompt to local Ollama (qwen2.5-coder:7b): '{user_prompt}'...\n")

    response = ollama.chat(
        model="qwen2.5-coder:7b",  # Updated to the local coding model
        messages=[
            {
                "role": "system",
                "content": "You are an expert senior software engineer.",
            },
            {"role": "user", "content": user_prompt},
        ],
    )

    return response["message"]["content"]


if __name__ == "__main__":
    # Let's ask it a coding question
    reply = ask_local_llm("Write a Python function to reverse a string.")
    print("Response:")
    print(reply)
