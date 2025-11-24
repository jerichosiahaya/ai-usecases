from src.repository.llm.llm_service import LLMService
from src.repository.cosmos_db import CosmosDBRepository
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, AgentResponseItem
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.chat_history import ChatHistory
from loguru import logger
import json

class CaseChatUseCase:
    def __init__(self, llm_repository: LLMService, cosmos_db: CosmosDBRepository = None):
        self.llm_service = llm_repository
        self.cosmos_db = cosmos_db
        self.case_analyst_agent = self.llm_service.create_case_analyst_agent()

    async def chat(self, messages: list[dict], session_id: str, case_id: str = None) -> dict:
        """
        Chat with case context
        
        Args:
            messages: List of chat messages
            session_id: Session identifier
            case_id: Case ID to fetch details from Cosmos DB
        """
        
        # Fetch case details if case_id is provided
        case_context = ""
        if case_id and self.cosmos_db:
            try:
                case = self.cosmos_db.get_case_by_id(case_id)
                case_context = f"""\n\nCase ID: {case_id}\n
                Case Context:\nTitle: {case.get('name', 'N/A')}\n
                Description: {case.get('description', 'N/A')}"""
            except Exception as e:
                logger.warning(f"Could not fetch case details for {case_id}: {e}")
        
        # Build chat messages with case context
        chat_messages = []
        for idx, msg in enumerate(messages):

            if idx == 0 and case_context:
                chat_content = ChatMessageContent(
                    role=AuthorRole.SYSTEM,
                    items=[
                        TextContent(text=case_context)
                    ]
                )
                chat_messages.append(chat_content)

            if msg["role"].lower() == "user":
                role = AuthorRole.USER
            elif msg["role"].lower() == "assistant" or msg["role"].lower() == "bot":
                role = AuthorRole.ASSISTANT
            elif msg["role"].lower() == "system":
                role = AuthorRole.SYSTEM
            else:
                role = AuthorRole.USER
            
            chat_content = ChatMessageContent(
                role=role,
                items=[
                    TextContent(text=msg["text"])
                ]
            )
            chat_messages.append(chat_content)

        response = await self.case_analyst_agent.get_response(
            messages=chat_messages
        )

        response_json = json.loads(str(response))

        return response_json


# async def test_case_chat():
#     """Test the CaseChatUseCase functionality"""
#     try:
#         from src.config.env import AppConfig
#         from src.repository.llm.llm_service import LLMService
#         from src.repository.cosmos_db import CosmosDBRepository
        
#         # Initialize services
#         llm_service = LLMService(config=AppConfig)
#         cosmos_db = CosmosDBRepository(AppConfig.COSMOS_DB_CONNECTION_STRING)
        
#         # Create the chat use case with Cosmos DB
#         chat_usecase = CaseChatUseCase(llm_repository=llm_service, cosmos_db=cosmos_db)
        
#         # Test messages
#         test_messages = [
#             {
#                 "role": "user",
#                 "text": "Apa yang terjadi dengan Agri Sentosa dan Food Supply?"
#             }
#         ]
        
#         # Use a real case_id or None for testing without case context
#         test_case_id = "448c8ed3-1ec8-42fb-b46b-739bbdab70a8"  # Replace with actual case ID
        
#         print(f"\n{'='*60}")
#         print("Testing CaseChatUseCase with Case Context")
#         print(f"{'='*60}\n")
#         print(f"Query: {test_messages[0]['text']}\n")
#         if test_case_id != "your-case-id-here":
#             print(f"Case ID: {test_case_id}\n")
        
#         # Perform chat
#         response = await chat_usecase.chat(
#             messages=test_messages, 
#             session_id="test-session",
#             case_id=test_case_id
#         )
        
#         print(f"\nResponse received:")
#         print(json.dumps(response, indent=2, ensure_ascii=False))
#         print(f"\n{'='*60}\n")
        
#     except Exception as e:
#         logger.error(f"Test failed: {e}")
#         print(f"Error: {e}")


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_case_chat())
