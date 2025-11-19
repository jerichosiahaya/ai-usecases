from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from loguru import logger
from src.llm.prompt import _get_cv_extractor_system_prompt, _get_predefined_score_system_prompt
from src.domain.cv_extractor import CVAttributeExtractionResponse
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
import json
from src.domain.cv_scoring import CVScoringResponse, CVScoringAttribute

class LLMService:
    def __init__(self, service_id: str = "default_service", azure_openai_key=None, azure_openai_endpoint=None, azure_openai_deployment=None, azure_openai_version=None):

        self.azure_chat_completion = AzureChatCompletion(
            service_id=service_id,
            deployment_name=azure_openai_deployment,
            api_version=azure_openai_version,
            api_key=azure_openai_key,
            endpoint=azure_openai_endpoint
        )

    async def extract_cv_attributes(self, cv_text: str) -> dict:
        try:
            instructions = _get_cv_extractor_system_prompt()
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = CVAttributeExtractionResponse

            prompt = f"""
            Here is the CV text:
            {cv_text}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="CVExtractorAgent",
                instructions=instructions,
                arguments=KernelArguments(settings=settings)
            ) 

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))
        
        except Exception as e:
            raise Exception(f"Error extracting CV attributes: {str(e)}")
        
    async def score_cv(self, predefined_score: str, candidate_data: str) -> str:
        try:
            instructions = _get_predefined_score_system_prompt(predefined_score)
            settings = OpenAIChatPromptExecutionSettings()
            settings.response_format = CVScoringResponse

            prompt = f"""
            Candidate:
            {candidate_data}
            """

            chat_content = ChatMessageContent(
                role=AuthorRole.USER,
                items=[
                    TextContent(text=prompt)
                ]
            )

            agent = ChatCompletionAgent(
                service=self.azure_chat_completion,
                name="CVScoringAgent",
                instructions=instructions,
                arguments=KernelArguments(settings=settings)
            )

            response = await agent.get_response(chat_content)

            return json.loads(str(response.content))

        except Exception as e:
            raise Exception(f"Error scoring CV: {str(e)}")


