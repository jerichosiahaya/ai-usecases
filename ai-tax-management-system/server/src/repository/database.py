from azure.cosmos import CosmosClient, exceptions
from loguru import logger
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class AzureCosmosDBRepository:
    """
    Generic repository for Azure Cosmos DB operations.
    Provides CRUD operations for any document type.
    """
    
    def __init__(self, connection_string: str, database_id: str, container_id: str):
        """
        Initialize Cosmos DB repository
        
        Args:
            connection_string: Cosmos DB connection string
            database_id: Database name
            container_id: Container name
        """
        try:
            self.client = CosmosClient.from_connection_string(connection_string)
            self.database = self.client.get_database_client(database_id)
            self.container = self.database.get_container_client(container_id)
            logger.info(f"Connected to Cosmos DB database '{database_id}', container '{container_id}'")
        except Exception as e:
            logger.error(f"Failed to connect to Cosmos DB: {e}")
            raise

    def create_document(self, document_data: Dict[str, Any], partition_key: Optional[str] = None, container_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new document in Cosmos DB
        
        Args:
            document_data: Document data to store
            document_type: Type identifier for the document
            partition_key: Optional partition key value. If not provided, uses document id
            
        Returns:
            Created document with id and timestamps
        """
        try:
            container = self.database.get_container_client(container_id) if container_id else self.container

            doc_id = document_data.get("id") or str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            document = {
                **document_data,
                "id": doc_id,
                "created_at": document_data.get("created_at", now),
                "updated_at": now
            }
            
            # Add partition key field if specified and different from id
            if partition_key and partition_key != doc_id:
                document[partition_key] = document.get(partition_key, doc_id)
            
            created = container.create_item(body=document)
            return created
        except exceptions.CosmosHttpResponseError as e:
            raise
        except Exception as e:
            raise

    def get_document_by_id(self, document_id: str, partition_key: Optional[str] = None, container_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a specific document by ID
        
        Args:
            document_id: Document ID to retrieve
            partition_key: Partition key value. If not provided, uses document_id
            
        Returns:
            Retrieved document
        """
        try:
            container = self.database.get_container_client(container_id) if container_id else self.container
            pk = partition_key if partition_key else document_id
            item = container.read_item(item=document_id, partition_key=pk)
            logger.info(f"Retrieved document: {document_id}")
            return item
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Document not found: {document_id}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            raise

    def query_documents(
        self, 
        document_type: Optional[str] = None,
        query_filter: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        order_by: str = "created_at DESC",
        max_items: Optional[int] = None,
        container_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents with optional filters
        
        Args:
            document_type: Filter by document type
            query_filter: Additional SQL WHERE clause (without WHERE keyword)
            parameters: Query parameters for parameterized queries
            order_by: ORDER BY clause (without ORDER BY keyword)
            max_items: Maximum number of items to return
            
        Returns:
            List of matching documents
        """
        try:
            container = self.database.get_container_client(container_id) if container_id else self.container
            
            # Build query
            query = "SELECT * FROM c"
            
            conditions = []
            if document_type:
                conditions.append(f"c.type = '{document_type}'")
            if query_filter:
                conditions.append(query_filter)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            if order_by:
                query += f" ORDER BY c.{order_by}"
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
                max_item_count=max_items
            ))
            
            logger.info(f"Retrieved {len(items)} documents (type: {document_type or 'all'})")
            return items
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise

    def delete_document(self, document_id: str, partition_key: Optional[str] = None) -> bool:
        """
        Delete a document from Cosmos DB
        
        Args:
            document_id: Document ID to delete
            partition_key: Partition key value. If not provided, uses document_id
            
        Returns:
            True if deletion was successful
        """
        try:
            pk = partition_key if partition_key else document_id
            self.container.delete_item(item=document_id, partition_key=pk)
            logger.info(f"Deleted document: {document_id}")
            return True
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Document not found for deletion: {document_id}")
            raise
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise

    def update_document(
        self, 
        document_id: str, 
        update_data: Dict[str, Any],
        partition_key: Optional[str] = None,
        partial_update: bool = True,
        container_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing document
        
        Args:
            document_id: Document ID to update
            update_data: Data to update (merged with existing if partial_update=True)
            partition_key: Partition key value. If not provided, uses document_id
            partial_update: If True, merge with existing data. If False, replace entire document.
            
        Returns:
            Updated document
        """
        try:
            container = self.database.get_container_client(container_id) if container_id else self.container
            pk = partition_key if partition_key else document_id
            
            if partial_update:
                # Get existing document and merge
                existing = self.get_document_by_id(document_id, partition_key, container_id)
                
                # Update fields (preserve id and created_at)
                for key, value in update_data.items():
                    if key not in ["id", "created_at"]:
                        existing[key] = value
                
                document = existing
            else:
                # Replace entire document
                document = {
                    **update_data,
                    "id": document_id
                }
            
            # Update timestamp
            document["updated_at"] = datetime.utcnow().isoformat()
            
            updated = container.upsert_item(body=document)
            logger.info(f"Updated document: {document_id}")
            return updated
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            raise
    
    def upsert_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a document (upsert operation)
        
        Args:
            document_data: Complete document data including id
            
        Returns:
            Upserted document
        """
        try:
            document_data["updated_at"] = datetime.utcnow().isoformat()
            
            if "created_at" not in document_data:
                document_data["created_at"] = document_data["updated_at"]
            
            upserted = self.container.upsert_item(body=document_data)
            logger.info(f"Upserted document: {document_data.get('id')}")
            return upserted
        except Exception as e:
            logger.error(f"Error upserting document: {e}")
            raise
