"""Railway-friendly entrypoint that reads the assigned PORT directly."""

from __future__ import annotations

import os

import uvicorn


def main() -> int:
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT") or os.environ.get("API_PORT") or "8000")
    uvicorn.run("aabw_agent.api:app", host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
