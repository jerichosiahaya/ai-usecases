from enum import Enum

class ResponseStatus(str, Enum):
    Success = "Success"
    Failed = "Failed"
    Error = "Error"

class FinancialAgentName(str, Enum):
    DataAnalyst = "DataAnalystAgent"
    BusinessAnalyst = "BusinessAnalystAgent"
    Orchestrator = "OrchestratorAgent"
    DataVisualizer = "DataVisualizerAgent"

class MarketIntelligenceAgentName(str, Enum):
    MarketAnalyst = "MarketAnalystAgent"

class FinancialIntentResponse(str, Enum):
    Financial = "FINANCIAL"
    Greeting = "GREETING"
    Market = "MARKET"
