import asyncio
import argparse
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
import uvicorn

from src.delivery.upload_routes import router as upload_router
from src.delivery.status_routes import router as status_router
from src.config.dependencies import (
    get_app_config,
    get_content_understanding_repository,
    get_blob_storage_repository
)


# Worker function
async def run_worker():
    """
    Background worker for processing tasks
    """
    logger.info("Worker started")
    try:
        while True:
            # TODO: Implement your worker logic here
            # Examples:
            # - Process queue messages
            # - Handle background tasks
            # - Process uploaded files
            await asyncio.sleep(10)  # Placeholder - replace with actual work
            logger.debug("Worker heartbeat")
    except asyncio.CancelledError:
        logger.info("Worker shutting down...")
        raise
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Application starting up...")
    
    # Initialize singletons at startup to fail fast and reduce first request latency
    logger.info("Initializing Azure client singletons...")
    config = get_app_config()
    get_content_understanding_repository(config)
    get_blob_storage_repository(config)
    logger.info("Azure client singletons initialized successfully")
    
    # Start the worker task only if running in 'both' mode
    # (when running http-only, worker won't start here)
    worker_task = asyncio.create_task(run_worker())
    logger.info("Background worker task created")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info("Worker task cancelled successfully")


# Create FastAPI app
app = FastAPI(
    title="AI Tax Management System",
    description="API for tax document processing and management",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(upload_router)
app.include_router(status_router)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "AI Tax Management System",
        "version": "0.1.0",
        "status": "running"
    }


async def run_worker_standalone():
    """
    Run worker in standalone mode
    """
    logger.info("Starting worker in standalone mode...")
    try:
        await run_worker()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        raise


def run_http_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run HTTP server
    """
    logger.info(f"Starting HTTP server on {host}:{port}...")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="AI Tax Management System - Server"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["http", "worker", "both"],
        default="http",
        help="Run mode: 'http' for API server only, 'worker' for background worker only, 'both' for combined"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host address for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP server (default: 8000)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO"
    )
    
    logger.info(f"Starting application in '{args.mode}' mode")
    
    # Run based on mode
    if args.mode == "worker":
        # Run only the worker
        asyncio.run(run_worker_standalone())
    elif args.mode == "http":
        # Run only the HTTP server (worker won't start in lifespan)
        # Create app without worker in lifespan for http-only mode
        app_http_only = FastAPI(
            title="AI Tax Management System",
            description="API for tax document processing and management",
            version="0.1.0"
        )
        app_http_only.include_router(upload_router)
        app_http_only.include_router(status_router)
        
        @app_http_only.get("/")
        async def root():
            return {
                "service": "AI Tax Management System",
                "version": "0.1.0",
                "status": "running",
                "mode": "http-only"
            }
        
        uvicorn.run(
            app_http_only,
            host=args.host,
            port=args.port,
            log_level="info"
        )
    elif args.mode == "both":
        # Run HTTP server with worker in lifespan
        run_http_server(host=args.host, port=args.port)
