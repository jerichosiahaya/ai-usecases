from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from loguru import logger
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
import json
from typing import Optional, Any

from src.config.env import AppConfig
from src.repository.prompt.cases import (
    get_case_analyst_chat_system_prompt
)
from src.repository.llm.llm_tools import CaseAnalystAgentTools
from src.domain.cases import CaseChatResponse

class LLMService:
    def __init__(self, service_id: str = "default_service", config: AppConfig = None):

        self.azure_chat_completion = AzureChatCompletion(
            service_id=service_id,
            deployment_name=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_version=config.AZURE_OPENAI_API_VERSION,
            api_key=config.AZURE_OPENAI_API_KEY,
            endpoint=config.AZURE_OPENAI_API_BASE
        )

        self.case_analyst_tools = CaseAnalystAgentTools(config=config)

    def create_case_analyst_agent(self):
        settings = OpenAIChatPromptExecutionSettings()
        settings.response_format = CaseChatResponse
        instruction = get_case_analyst_chat_system_prompt()
        kernel = Kernel()
        kernel.add_plugin(self.case_analyst_tools, plugin_name="CaseAnalystTools")
        return ChatCompletionAgent(
            service=self.azure_chat_completion,
            kernel=kernel,
            name="CaseAnalystAgent",
            instructions=instruction,
            arguments=KernelArguments(settings=settings)
        )
    
    # def create_orchestrator_agent(self):
    #     settings = OpenAIChatPromptExecutionSettings()
    #     settings.response_format = IntentResponse
    #     instruction = get_financial_orchestrator_chat_system_prompt()
    #     return ChatCompletionAgent(
    #         service=self.azure_chat_completion,
    #         name=FinancialAgentName.Orchestrator.value,
    #         instructions=instruction,
    #         arguments=KernelArguments(settings=settings)
    #     )
    
    # def create_business_analyst_agent(self):
    #     settings = OpenAIChatPromptExecutionSettings()
    #     settings.response_format = BusinessAnalystResponse
    #     instruction = get_financial_business_analyst_chat_system_prompt()
    #     return ChatCompletionAgent(
    #         service=self.azure_chat_completion,
    #         name=FinancialAgentName.BusinessAnalyst.value,
    #         instructions=instruction,
    #         arguments=KernelArguments(settings=settings)
    #     )

    # async def agent_communication(self, sender_agent: ChatCompletionAgent, receiver_agent: ChatCompletionAgent, message: list[ChatMessageContent], context: Optional[Any] = None):
    #     try:
    #         # add data context if sender is data analyst and receiver is business analyst
    #         if (sender_agent.name == FinancialAgentName.DataAnalyst.value and receiver_agent.name == FinancialAgentName.BusinessAnalyst.value) or (sender_agent.name == FinancialAgentName.BusinessAnalyst.value and receiver_agent.name == FinancialAgentName.DataVisualizer.value):
    #             enhanced_messages = message.copy()
    #             if context is not None:
    #                 context_text = f"Data context:\n{json.dumps(context, indent=2, default=str)}"
    #                 context_message = ChatMessageContent(
    #                     role=AuthorRole.SYSTEM,
    #                     items=[TextContent(text=context_text)]
    #                 )
    #                 # Insert context message before the last message (which is usually the user's query)
    #                 enhanced_messages.insert(-1, context_message) 
                                   
    #             response = await receiver_agent.get_response(enhanced_messages)
    #         else:
    #             response = await receiver_agent.get_response(message)
    #         response_content = str(response.content)
    #         try:
    #             return json.loads(response_content)
    #         except json.JSONDecodeError:
    #             # Try to extract the first valid JSON object
    #             try:
    #                 return self._extract_first_valid_json(response_content)
    #             except ValueError:
    #                 # If JSON extraction fails, return the raw content for business analyst responses
    #                 if receiver_agent.name == FinancialAgentName.BusinessAnalyst.value:
    #                     # Try to wrap raw content in expected format
    #                     return {"analysis": response_content}
    #                 elif receiver_agent.name == FinancialAgentName.DataAnalyst.value:
    #                     # For data analyst, we need a SQL query
    #                     return {"sql_query": response_content}
    #                 else:
    #                     return response_content
                
    #     except Exception as e:
    #         logger.error(f"Error in agent communication: {e}")
    #         raise ValueError(f"Failed to process agent response: {str(e)}")
    
    # def _extract_first_valid_json(self, content: str) -> dict:
    #     import re
        
    #     # Clean the content - remove any markdown formatting
    #     cleaned_content = content.strip()
    #     cleaned_content = re.sub(r'```json\s*', '', cleaned_content)
    #     cleaned_content = re.sub(r'```\s*', '', cleaned_content)
        
    #     # Try to find JSON objects using regex
    #     json_pattern = r'\{[^{}]*\}'
    #     matches = re.findall(json_pattern, cleaned_content)
        
    #     for match in matches:
    #         try:
    #             parsed = json.loads(match)
    #             logger.info(f"Successfully extracted first valid JSON: {parsed}")
    #             return parsed
    #         except json.JSONDecodeError:
    #             continue
        
    #     # If no valid JSON found, try line by line
    #     lines = cleaned_content.split('\n')
    #     for line in lines:
    #         line = line.strip()
    #         if line.startswith('{') and line.endswith('}'):
    #             try:
    #                 parsed = json.loads(line)
    #                 logger.info(f"Successfully extracted JSON from line: {parsed}")
    #                 return parsed
    #             except json.JSONDecodeError:
    #                 continue
        
    #     # If still no valid JSON, return error
    #     logger.error(f"Could not extract valid JSON from content: {content}")
    #     raise ValueError("No valid JSON object found in the content")
    
    