from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import asyncio
from src.repository.llm.llm_service import LLMService
from src.config.env import AppConfig
from src.domain.http_response import ok, bad_request_error, internal_server_error
from loguru import logger
from src.repository.sql_server import SqlServerRepository
from src.repository.cosmos_db import CosmosDBRepository
from src.repository.blob_storage import BlobStorageRepository
from src.repository.service_bus import ServiceBusRepository
from src.routes.cases import init_cases_routes
from src.routes.upload import init_upload_routes

app = Flask(__name__)
CORS(app)

config = AppConfig()

# Initialize Cosmos DB Repository
try:
    cosmos_db = CosmosDBRepository(
        connection_string=config.COSMOS_DB_CONNECTION_STRING
    )
except Exception as e:
    logger.warning(f"Cosmos DB not configured: {e}")
    cosmos_db = None

# Initialize Blob Storage Repository
try:
    blob_storage = BlobStorageRepository(
        connection_string=config.AZURE_STORAGE_CONNECTION_STRING
    )
except Exception as e:
    logger.warning(f"Blob Storage not configured: {e}")
    blob_storage = None

# Initialize Service Bus Repository
try:
    service_bus = ServiceBusRepository(
        connection_string=config.SERVICE_BUS_CONNECTION_STRING
    )
except Exception as e:
    logger.warning(f"Service Bus not configured: {e}")
    service_bus = None

# Register case routes
if cosmos_db:
    cases_routes = init_cases_routes(cosmos_db, service_bus)
    app.register_blueprint(cases_routes)

# Register upload routes
if blob_storage:
    upload_routes = init_upload_routes(blob_storage, cosmos_db)
    app.register_blueprint(upload_routes)

sql_server = SqlServerRepository(
    connection_string=config.SQL_SERVER_CONNECTION_STRING
)

@app.route('/ping', methods=['GET'])
def ping():
    return ok(message="pong", data={"timestamp": datetime.utcnow().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)