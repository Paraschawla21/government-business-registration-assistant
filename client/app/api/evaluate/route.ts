import { NextResponse } from "next/server";

const PYTHON_BACKEND_URL =
  process.env.PYTHON_BACKEND_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { tool_name?: unknown };

    if (typeof body.tool_name !== "string" || !body.tool_name.trim()) {
      return NextResponse.json(
        { detail: "tool_name is required" },
        { status: 400 },
      );
    }

    const response = await fetch(`${PYTHON_BACKEND_URL}/api/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool_name: body.tool_name.trim() }),
      cache: "no-store",
    });

    const responseBody = await response.text();

    return new NextResponse(responseBody, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch {
    return NextResponse.json(
      { detail: "The Python backend could not be reached." },
      { status: 502 },
    );
  }
}
