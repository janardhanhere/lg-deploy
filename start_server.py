import os
import sys

if __name__ == "__main__":
    # Use uvicorn to run the FastAPI app
    # Allow host/port to be set via environment variables
    host = os.environ.get("LG_DEPLOY_HOST", "127.0.0.1")
    port = int(os.environ.get("LG_DEPLOY_PORT", 8000))
    reload = os.environ.get("LG_DEPLOY_RELOAD", "false").lower() == "true"

    try:
        import uvicorn
    except ImportError:
        print("Uvicorn is not installed. Please install it with 'pip install uvicorn'.")
        sys.exit(1)

    uvicorn.run(
        "src.lg_deploy.main:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True
    )
