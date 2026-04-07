"""Compatibility entrypoint for running the FastAPI app from ``src/main.py``."""

from app.api.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
