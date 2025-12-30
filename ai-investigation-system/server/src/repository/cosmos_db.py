import os
from azure.cosmos import CosmosClient
from loguru import logger
import uuid
from datetime import datetime
from src.models.case import CaseModel


class CosmosDBRepository:
    def __init__(self, connection_string: str, database_id: str, container_id: str):
        try:
            self.client = CosmosClient.from_connection_string(connection_string)
            self.database = self.client.get_database_client(database_id)
            self.container = self.database.get_container_client(container_id)
            logger.info(f"Connected to Cosmos DB database '{database_id}', container '{container_id}'")
        except Exception as e:
            logger.error(f"Failed to connect to Cosmos DB: {e}")
            raise

    def create_case(self, case_data: dict) -> dict:
        """Create a new case in Cosmos DB"""
        try:
            case_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            # Process files to ensure they have the correct schema
            files = []
            for file_item in case_data.get("files", []):
                if isinstance(file_item, dict):
                    files.append({
                        "url": file_item.get("url") or file_item.get("name"),
                        "name": file_item.get("name"),
                        "description": file_item.get("description", ""),
                        "classification": file_item.get("classification", ""),
                        "format": file_item.get("format")
                    })
            
            document = {
                "id": case_id,
                "name": case_data.get("name"),
                "description": case_data.get("description"),
                "status": case_data.get("status", "pending"),
                "files": files,
                "case_main_category": case_data.get("case_main_category"),
                "case_sub_category": case_data.get("case_sub_category"),
                "analysis": case_data.get("analysis"),
                "applicable_laws": case_data.get("applicable_laws", []),
                "law_impact_analysis": case_data.get("law_impact_analysis", ""),
                "insights": case_data.get("insights"),
                "recommendations": case_data.get("recommendations"),
                "created_at": now,
                "updated_at": now,
                "type": "case",
                "caseId": case_id
            }
            
            self.container.create_item(body=document)
            logger.info(f"Created case with ID: {case_id}")
            return document
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            raise

    def get_case_by_id(self, case_id: str) -> dict:
        """Get a specific case by ID"""
        try:
            item = self.container.read_item(item=case_id, partition_key=case_id)
            logger.info(f"Retrieved case: {case_id}")
            return item
        except Exception as e:
            logger.error(f"Error retrieving case {case_id}: {e}")
            raise

    def get_all_cases(self) -> list:
        """Get all cases from Cosmos DB"""
        try:
            query = "SELECT * FROM c WHERE c.type = 'case' ORDER BY c.created_at DESC"
            items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
            logger.info(f"Retrieved {len(items)} cases")
            return items
        except Exception as e:
            logger.error(f"Error retrieving cases: {e}")
            raise

    def delete_case(self, case_id: str) -> bool:
        """Delete a case from Cosmos DB"""
        try:
            self.container.delete_item(item=case_id, partition_key=case_id)
            logger.info(f"Deleted case: {case_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting case {case_id}: {e}")
            raise

    def update_case(self, case_id: str, case_data: dict) -> dict:
        """Update an existing case"""
        try:
            existing_case = self.get_case_by_id(case_id)
            
            # Process files if provided
            if "files" in case_data:
                files = []
                for file_item in case_data.get("files", []):
                    if isinstance(file_item, dict):
                        files.append({
                            "url": file_item.get("url") or file_item.get("name"),
                            "name": file_item.get("name"),
                            "description": file_item.get("description", ""),
                            "classification": file_item.get("classification", ""),
                            "format": file_item.get("format")
                        })
                case_data["files"] = files
            
            # Update fields
            for key, value in case_data.items():
                if key not in ["id", "created_at"]:
                    existing_case[key] = value
            
            existing_case["updated_at"] = datetime.utcnow().isoformat()
            
            self.container.upsert_item(body=existing_case)
            logger.info(f"Updated case: {case_id}")
            return existing_case
        except Exception as e:
            logger.error(f"Error updating case {case_id}: {e}")
            raise
