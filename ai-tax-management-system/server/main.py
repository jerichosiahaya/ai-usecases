import asyncio
import argparse
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn
from azure.servicebus.aio import ServiceBusClient, AutoLockRenewer

from src.delivery.upload_routes import router as upload_router
from src.delivery.status_routes import router as status_router
from src.delivery.tax_management import router as tax_management_router
from src.config.dependencies import (
    get_app_config,
    get_content_understanding_repository,
    get_azure_blob_storage_repository,
    get_rabbitmq_repository,
    get_minio_storage_repository,
    get_azure_service_bus_repository,
    get_content_extraction_service,
    get_llm_service_repository,
    get_azure_cosmos_repository
)

from src.common.const import Environment


# Worker function
async def run_worker():

    logger.info("Worker started")
    
    config = get_app_config()
    connection_string = config.AZURE_SERVICE_BUS_CONNECTION_STRING
    queue_name = config.AZURE_SERVICE_BUS_QUEUE_NAME
    
    if not connection_string:
        logger.error("SERVICE_BUS_CONNECTION_STRING not configured")
        return
    
    if not queue_name:
        logger.error("SERVICE_BUS_QUEUE_NAME not configured")
        return
    
    # Initialize content extraction service
    content_extraction = get_content_extraction_service(
        content_understanding_repo=get_content_understanding_repository(config),
        blob_storage_repo=get_azure_blob_storage_repository(config),
        rabbitmq_repo=get_rabbitmq_repository(config),
        minio_storage_repo=get_minio_storage_repository(config),
        llm_service_repo=get_llm_service_repository(config),
        azure_cosmos_repo=get_azure_cosmos_repository(config)
    )
    
    try:
        client = ServiceBusClient.from_connection_string(connection_string)
        renewer = AutoLockRenewer(max_lock_renewal_duration=3600)
        while True:
            try:
                async with client:
                    # Use max_lock_renewal_duration to automatically renew the message lock
                    # This allows processing to take up to 5 minutes without losing the lock
                    async with client.get_queue_receiver(
                        queue_name, 
                        max_wait_time=1,
                        auto_lock_renewer=renewer
                    ) as receiver:
                        logger.info(f"Connected to Service Bus queue: {queue_name}")
                        async for message in receiver:
                            try:
                                logger.info(f"Received message: {message.message_id}")
                                
                                # Parse message body - handle generator case
                                body = message.body
                                if hasattr(body, '__iter__') and not isinstance(body, (str, dict, bytes)):
                                    # It's a generator or iterator, join it
                                    body = b''.join(body).decode('utf-8')
                                elif isinstance(body, bytes):
                                    body = body.decode('utf-8')
                                
                                # Parse JSON if string
                                if isinstance(body, str):
                                    data = json.loads(body)
                                else:
                                    data = body
                                
                                logger.debug(f"Message data: {data}")
                                
                                await receiver.complete_message(message)
                                # Process the message using content extraction service
                                await content_extraction.process_message(data)
                                
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
                                # Don't try to complete if message processing failed
                                # The message will be retried automatically after lock expiration
                                
            except Exception as e:
                logger.error(f"Connection error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
                
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
    logger.info("Initializing client singletons...")
    config = get_app_config()
    get_content_understanding_repository(config)
    get_azure_blob_storage_repository(config)
    get_llm_service_repository(config)
    
    # Initialize RabbitMQ and MinIO only in development environment
    if config.ENV.lower() == Environment.Development.value:
        logger.info("Development environment detected - initializing RabbitMQ and MinIO...")
        get_rabbitmq_repository(config)
        get_minio_storage_repository(config)
        logger.info("RabbitMQ and MinIO initialized")
    else:
        logger.info(f"Skipping RabbitMQ and MinIO initialization (ENV={config.ENV})")
    
    logger.info("All client singletons initialized successfully")
    
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        
        # Add CORS middleware
        app_http_only.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        app_http_only.include_router(upload_router)
        app_http_only.include_router(status_router)
        app_http_only.include_router(tax_management_router)
        
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
