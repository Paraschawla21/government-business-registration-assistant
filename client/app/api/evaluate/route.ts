import { NextResponse } from "next/server";

const PYTHON_BACKEND_URL =
  process.env.PYTHON_BACKEND_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      businessType?: unknown;
      industry?: unknown;
      state?: unknown;
      city?: unknown;
      employees?: unknown;
      turnover?: unknown;
      activity?: unknown;
      operations?: unknown;
      gstin?: unknown;
      pan?: unknown;
    };

    if (typeof body.businessType !== "string" || !body.businessType.trim()) {
      return NextResponse.json(
        { detail: "businessType is required" },
        { status: 400 },
      );
    }

    if (typeof body.industry !== "string" || !body.industry.trim()) {
      return NextResponse.json({ detail: "industry is required" }, { status: 400 });
    }

    if (typeof body.state !== "string" || !body.state.trim()) {
      return NextResponse.json({ detail: "state is required" }, { status: 400 });
    }

    if (typeof body.city !== "string" || !body.city.trim()) {
      return NextResponse.json({ detail: "city is required" }, { status: 400 });
    }

    if (
      typeof body.employees !== "number" ||
      Number.isNaN(body.employees) ||
      body.employees < 0
    ) {
      return NextResponse.json(
        { detail: "employees must be a non-negative number" },
        { status: 400 },
      );
    }

    if (typeof body.turnover !== "string" || !body.turnover.trim()) {
      return NextResponse.json({ detail: "turnover is required" }, { status: 400 });
    }

    if (typeof body.activity !== "string" || body.activity.trim().length < 10) {
      return NextResponse.json(
        { detail: "activity must be at least 10 characters" },
        { status: 400 },
      );
    }

    if (typeof body.operations !== "string" || !body.operations.trim()) {
      return NextResponse.json({ detail: "operations is required" }, { status: 400 });
    }

    const response = await fetch(`${PYTHON_BACKEND_URL}/api/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        businessType: body.businessType.trim(),
        industry: body.industry.trim(),
        state: body.state.trim(),
        city: body.city.trim(),
        employees: body.employees,
        turnover: body.turnover.trim(),
        activity: body.activity.trim(),
        operations: body.operations.trim(),
        gstin:
          typeof body.gstin === "string" && body.gstin.trim()
            ? body.gstin.trim().toUpperCase()
            : null,
        pan:
          typeof body.pan === "string" && body.pan.trim()
            ? body.pan.trim().toUpperCase()
            : null,
      }),
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
