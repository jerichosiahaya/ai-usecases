import os
import asyncio
import json
import httpx
from io import BytesIO
from azure.servicebus.aio import ServiceBusClient
from azure.cosmos import CosmosClient
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
import PyPDF2
from docx import Document
import tiktoken
from llm_sk import LLMService, CaseDetails, CaseFile, AnalysisResult, FileDescriptionResult, KnowledgeGraphResult
from utils import convert_knowledge_graph_to_dict_format

CONNECTION_STRING = os.getenv("SERVICE_BUS_CONNECTION_STRING")
QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME", "ai-fraud")
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
COSMOS_DATABASE_NAME = os.getenv("COSMOS_DATABASE_NAME", "ai-fraud")
COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER_NAME", "cases")
COSMOS_VECTOR_CONTAINER = "vectors"

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

MAX_TOKENS = 8000


def truncate_text_to_tokens(text: str, max_tokens: int = 8000) -> str:
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
            text = encoding.decode(tokens)
            print(f"Text truncated from {len(encoding.encode(text))} to {len(tokens)} tokens")
        
        return text
    except Exception as e:
        print(f"Error truncating text: {e}")
        words = text.split()
        return ' '.join(words[:int(max_tokens * 0.75)])


async def extract_text_from_file(file_url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            file_bytes = BytesIO(response.content)
            
        if file_url.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file_bytes)
            text = '\n'.join([page.extract_text() for page in reader.pages])
        elif file_url.endswith('.docx'):
            doc = Document(file_bytes)
            text = '\n'.join([para.text for para in doc.paragraphs])
        elif file_url.endswith('.txt'):
            text = response.content.decode('utf-8')
        else:
            return ""
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {file_url}: {e}")
        return ""

async def vectorize_text(text: str) -> list:
    try:
        text = truncate_text_to_tokens(text, MAX_TOKENS)
        
        kernel = Kernel()
        embedding_service = AzureTextEmbedding(
            deployment_name=AZURE_EMBEDDING_DEPLOYMENT,
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY
        )
        kernel.add_service(embedding_service)
        
        vector = await embedding_service.generate_embeddings(text)
        
        if hasattr(vector, 'tolist'):
            vector = vector.tolist()
        
        if isinstance(vector, list) and len(vector) > 0:
            if isinstance(vector[0], list):
                vector = vector[0]
        
        return vector
    except Exception as e:
        print(f"Error vectorizing text: {e}")
        return []


def get_case_from_cosmos(case_id):
    try:
        client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Direct read using partition key (fastest)
        item = container.read_item(item=case_id, partition_key=case_id)
        print(f"Retrieved case data: {item}")
        
        if "files" in item:
            files = item["files"]
            if isinstance(files, list):
                for idx, file_item in enumerate(files):
                    print(f"Processing file {idx}: {file_item}")
        
        return item
        
    except Exception as e:
        print(f"Error retrieving case from CosmosDB: {e}")
        return None

def insert_embeddings_to_cases(case_id, embeddings, extracted_text, file_url):
    try:
        client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_VECTOR_CONTAINER)
        
        if hasattr(embeddings, 'tolist'):
            embedding_list = embeddings.tolist()
        else:
            embedding_list = list(embeddings)
        
        if isinstance(embedding_list, list) and len(embedding_list) > 0 and isinstance(embedding_list[0], list):
            embedding_list = embedding_list[0]
        
        embedding_list = [float(x) for x in embedding_list]
        
        file_id = file_url.split('/')[-1].split('.')[0]
        
        item = {
            "id": f"{case_id}-{file_id}",
            "caseId": case_id,
            "embeddings": embedding_list,
            "content": extracted_text,
            "fileUrl": file_url,
            "fileName": file_url.split('/')[-1],
            "fileType": file_url.split('.')[-1],
            "vectorDimension": len(embedding_list),
            "vectorModel": AZURE_EMBEDDING_DEPLOYMENT,
            "processed_at": str(asyncio.get_event_loop().time())
        }
        
        container.upsert_item(body=item)
        print(f"Inserted embeddings for case: {case_id}, file: {file_url.split('/')[-1]}")
        
    except Exception as e:
        print(f"Error inserting embeddings to cases: {e}")

async def build_case_details(case_data: dict) -> tuple[CaseDetails, dict]:
    """Build CaseDetails object from case data retrieved from CosmosDB
    
    Returns:
        tuple containing CaseDetails and a dict mapping file URLs to filenames
    """
    try:
        case_files = []
        file_url_map = {}
        
        if "files" in case_data and case_data["files"]:
            for file_item in case_data["files"]:
                # Handle both old format (string URLs) and new format (file objects)
                if isinstance(file_item, str):
                    # Old format: just a URL string
                    file_url = file_item
                    file_name = file_item.split('/')[-1]
                elif isinstance(file_item, dict):
                    # New format: file metadata object with url, name, description, format
                    file_url = file_item.get("url")
                    file_name = file_item.get("name", "").split('/')[-1] or file_url.split('/')[-1]
                    file_format = file_item.get("format", "")
                    file_description = file_item.get("description", "")
                else:
                    continue
                
                extracted_text = await extract_text_from_file(file_url)
                if extracted_text:
                    case_files.append(CaseFile(
                        filename=file_name,
                        content=extracted_text
                    ))
                    file_url_map[file_name] = file_url
        
        case_details = CaseDetails(
            title=case_data.get("name", "Untitled Case"),
            description=case_data.get("description", ""),
            files=case_files
        )
        
        return case_details, file_url_map
    except Exception as e:
        print(f"Error building case details: {e}")
        raise

async def save_analysis_results(case_id: str, analysis_result: AnalysisResult):
    """Save LLM analysis results to CosmosDB"""
    try:
        client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Retrieve and update the case document
        item = container.read_item(item=case_id, partition_key=case_id)
        
        # Update analysis, insights, recommendations, and status fields
        item["analysis"] = {
            "data_review": analysis_result.analysis.data_review,
            "root_cause_analysis": analysis_result.analysis.root_cause_analysis,
            "hypothesis_testing": analysis_result.analysis.hypothesis_testing
        }
        item["case_main_category"] = analysis_result.case_main_category
        item["case_sub_category"] = analysis_result.case_sub_category
        
        # Convert applicable_laws objects to dictionaries
        applicable_laws_list = []
        if analysis_result.applicable_laws:
            for law in analysis_result.applicable_laws:
                applicable_laws_list.append({
                    "law_name": law.law_name,
                    "articles": law.articles,
                    "violation_description": law.violation_description,
                    "penalty_level": law.penalty_level
                })
        
        item["applicable_laws"] = applicable_laws_list
        item["law_impact_analysis"] = analysis_result.law_impact_analysis
        item["insights"] = analysis_result.insights
        item["recommendations"] = analysis_result.recommendations
        item["status"] = "completed"
        item["updated_at"] = str(asyncio.get_event_loop().time())
        
        container.replace_item(item=case_id, body=item)
        print(f"Saved analysis results for case: {case_id}")
        print(f"Status updated to: completed")
        print(f"Applicable laws: {len(applicable_laws_list)} law(s) identified")
        
    except Exception as e:
        print(f"Error saving analysis results: {e}")

async def update_file_description(case_id: str, file_url: str, description: str, classification: str = None):
    """Update file description and classification in CosmosDB"""
    try:
        client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Retrieve and update the case document
        item = container.read_item(item=case_id, partition_key=case_id)
        
        # Find and update the file with matching URL
        if "files" in item and item["files"]:
            for file_obj in item["files"]:
                if isinstance(file_obj, dict) and (file_obj.get("url") == file_url or file_obj.get("name") == file_url):
                    file_obj["description"] = description
                    if classification:
                        file_obj["classification"] = classification
                    break
        
        container.replace_item(item=case_id, body=item)
        print(f"Updated file description and classification for case: {case_id}, file: {file_url.split('/')[-1]}")
        
    except Exception as e:
        print(f"Error updating file description: {e}")

async def save_knowledge_graph(case_id: str, knowledge_graph_result: KnowledgeGraphResult):
    """Save knowledge graph to CosmosDB"""
    try:
        client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Retrieve and update the case document
        item = container.read_item(item=case_id, partition_key=case_id)
        
        # Convert list format to dict format with node/edge IDs
        kg_dict = convert_knowledge_graph_to_dict_format(knowledge_graph_result)
        
        # Update knowledge_graph field
        item["knowledge_graph"] = kg_dict
        item["updated_at"] = str(asyncio.get_event_loop().time())
        
        container.replace_item(item=case_id, body=item)
        print(f"Saved knowledge graph for case: {case_id}")
        
    except Exception as e:
        print(f"Error saving knowledge graph: {e}")

async def process_message(receiver, message):
    try:
        # Extract message body - handle generator case
        body = message.body
        if hasattr(body, '__iter__') and not isinstance(body, (str, dict)):
            # It's a generator or iterator, join it
            body = b''.join(body).decode('utf-8')
        
        # Parse JSON
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        case_id = data.get("case_id")
        print(f"Processing case: {case_id}")
        print(f"Message data: {data}")
        
        # Retrieve case data from CosmosDB and check status
        case_data = get_case_from_cosmos(case_id)
        
        if not case_data:
            print(f"Case not found: {case_id}")
            await receiver.complete_message(message)
            return
        
        # Validation: Check if case is already completed
        if case_data.get("status") == "completed":
            print(f"Case already completed, skipping: {case_id}")
            await receiver.complete_message(message)
            return
        
        if case_data and "files" in case_data:
            for file_item in case_data["files"]:
                # Extract URL from file metadata (handle both old and new format)
                if isinstance(file_item, str):
                    file_url = file_item
                elif isinstance(file_item, dict):
                    file_url = file_item.get("url") or file_item.get("name")
                else:
                    continue
                
                print(f"Processing file: {file_url}")
                extracted_text = await extract_text_from_file(file_url)
                
                if extracted_text:
                    vector_data = await vectorize_text(extracted_text)
                    if vector_data is not None and len(vector_data) > 0:
                        print(f"Successfully vectorized: {file_url}")
                        print(f"Vector dimension: {len(vector_data)}")
                        insert_embeddings_to_cases(case_id, vector_data, extracted_text, file_url)
        
        # Analyze case using LLM after retrieving all data
        if case_data:
            print(f"Building case details for LLM analysis...")
            case_details, file_url_map = await build_case_details(case_data)
            
            if case_details.files:
                print(f"Initializing LLM service for case analysis...")
                llm_service = LLMService(
                    service_id="fraud-analysis-service",
                    azure_openai_key=AZURE_OPENAI_KEY,
                    azure_openai_endpoint=AZURE_OPENAI_ENDPOINT,
                    azure_openai_deployment=AZURE_OPENAI_DEPLOYMENT,
                    azure_openai_version=AZURE_OPENAI_VERSION
                )
                
                # Step 1: Generate descriptions for each file
                print(f"Generating descriptions for {len(case_details.files)} file(s)...")
                for case_file in case_details.files:
                    try:
                        print(f"Analyzing file: {case_file.filename}")
                        
                        file_description_result = await llm_service.analyze_file_description(
                            case_file.filename,
                            case_file.content,
                            case_details
                        )
                        
                        # Update file description and classification in CosmosDB
                        file_url = file_url_map.get(case_file.filename)
                        if file_url:
                            await update_file_description(
                                case_id, 
                                file_url, 
                                file_description_result.description,
                                file_description_result.classification
                            )
                            print(f"File description and classification saved: {case_file.filename}")
                    except Exception as e:
                        print(f"Error analyzing file {case_file.filename}: {e}")
                
                # Step 2: Analyze the entire case
                print(f"Analyzing case with LLM...")
                
                analysis_result = await llm_service.analyze_case(case_details)
                
                print(f"Analysis complete. Saving results...")
                await save_analysis_results(case_id, analysis_result)
                print(f"Case analysis completed successfully: {case_id}")
                
                # Step 3: Generate knowledge graph
                print(f"Generating knowledge graph...")
                
                knowledge_graph_result = await llm_service.generate_knowledge_graph(case_details)
                
                print(f"Knowledge graph generated. Saving to CosmosDB...")
                await save_knowledge_graph(case_id, knowledge_graph_result)
                print(f"Knowledge graph saved successfully: {case_id}")
            else:
                print(f"No files found for case analysis: {case_id}")
        
        await receiver.complete_message(message)
    except Exception as e:
        print(f"Error processing message: {e}")


async def listen_to_queue():
    while True:
        try:
            client = ServiceBusClient.from_connection_string(CONNECTION_STRING)
            async with client:
                async with client.get_queue_receiver(QUEUE_NAME, max_wait_time=1) as receiver:
                    print(f"Connected to queue: {QUEUE_NAME}")
                    async for message in receiver:
                        await process_message(receiver, message)
        except Exception as e:
            print(f"Connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(listen_to_queue())
