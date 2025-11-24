import uuid
import pyodbc
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from typing import List, Optional
import pandas as pd
from loguru import logger

class SqlServerRepository:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._ensure_chat_history_table()

    async def execute_query(self, sql_query):
        try:
            conn = pyodbc.connect(self.connection_string)
            
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            
            if df.empty:
                return None
            
            return df.to_dict(orient='records')
            
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            return None
    
    def _ensure_chat_history_table(self):
        """Create chat_history table if it doesn't exist"""
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chat_history' AND xtype='U')
                CREATE TABLE chat_history (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    session_id NVARCHAR(100) NOT NULL,
                    user_id NVARCHAR(100) NULL,
                    timestamp DATETIME2 DEFAULT GETDATE(),
                    user_query NVARCHAR(MAX) NOT NULL,
                    query_intent NVARCHAR(20) NOT NULL,
                    processing_workflow NVARCHAR(50) NOT NULL,
                    coordinator_analysis NVARCHAR(MAX) NULL,
                    sql_query_generated NVARCHAR(MAX) NULL,
                    sql_execution_status NVARCHAR(20) NULL,
                    records_retrieved INT NULL,
                    final_response NVARCHAR(MAX) NOT NULL,
                    response_type NVARCHAR(20) NOT NULL,
                    total_processing_time_ms INT NULL,
                    database_calls_count INT DEFAULT 0,
                    agents_involved NVARCHAR(100) NULL,
                    error_occurred BIT DEFAULT 0,                    
                    error_message NVARCHAR(MAX) NULL,
                    error_step NVARCHAR(50) NULL,
                    available_metrics_count INT NULL,
                    financial_data_preview NVARCHAR(MAX) NULL,
                    output_token_count BIGINT NULL,
                    input_token_count BIGINT NULL,
                    total_token_count BIGINT NULL,
                    total_token_cost BIGINT NULL,
                    visualization_code NVARCHAR(MAX) NULL,
                    chart_type NVARCHAR(200) NULL,
                    visualization_explanation NVARCHAR(MAX) NULL,
                    INDEX IX_chat_history_session_timestamp (session_id, timestamp),
                    INDEX IX_chat_history_intent (query_intent),
                    INDEX IX_chat_history_user_timestamp (user_id, timestamp)
                );
            """)
            
            # Check if visualization columns exist and add them if not
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'chat_history' AND COLUMN_NAME = 'visualization_code')
                BEGIN
                    ALTER TABLE chat_history ADD visualization_code NVARCHAR(MAX) NULL;
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'chat_history' AND COLUMN_NAME = 'chart_type')
                BEGIN
                    ALTER TABLE chat_history ADD chart_type NVARCHAR(200) NULL;
                END
                ELSE
                BEGIN
                    -- Update chart_type column size if it's too small
                    IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'chat_history' AND COLUMN_NAME = 'chart_type' 
                              AND CHARACTER_MAXIMUM_LENGTH < 200)
                    BEGIN
                        ALTER TABLE chat_history ALTER COLUMN chart_type NVARCHAR(200) NULL;
                    END
                END
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_NAME = 'chat_history' AND COLUMN_NAME = 'visualization_explanation')
                BEGIN
                    ALTER TABLE chat_history ADD visualization_explanation NVARCHAR(MAX) NULL;
                END
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error creating chat history table: {str(e)}")
    
    async def add_message(self, session_id: str, user_id: str, user_query: str, 
                         intent: str, workflow: str, final_response: str, 
                         **kwargs) -> str:
        """Add a message to chat history"""
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            message_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO chat_history (
                    session_id, user_id, user_query, query_intent, processing_workflow,
                    sql_query_generated, sql_execution_status, records_retrieved, 
                    final_response, response_type, total_processing_time_ms, 
                    database_calls_count, agents_involved, error_occurred, 
                    error_message, available_metrics_count, input_token_count, 
                    output_token_count, total_token_count, total_token_cost,
                    visualization_code, chart_type, visualization_explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_id, user_query, intent, workflow,
                kwargs.get('sql_query'), kwargs.get('sql_status'), kwargs.get('records_count'),
                final_response, intent.lower(), kwargs.get('processing_time'),
                kwargs.get('db_calls', 0), kwargs.get('agents_used', ''), 
                1 if kwargs.get('error') else 0, kwargs.get('error'), 
                kwargs.get('metrics_count'), kwargs.get('input_token_count', 0),
                kwargs.get('output_token_count', 0), kwargs.get('total_token_count', 0), 
                kwargs.get('total_token_cost', 0),
                kwargs.get('visualization_code'), kwargs.get('chart_type'), kwargs.get('visualization_explanation')
            ))
            
            conn.commit()
            conn.close()
            
            return message_id
            
        except Exception as e:
            print(f"Error adding message to chat history: {str(e)}")
            return str(uuid.uuid4())
    
    async def get_messages(self, session_id: str, limit: int = 10) -> List[ChatMessageContent]:
        """Retrieve chat messages for a session"""
        try:
            conn = pyodbc.connect(self.connection_string)
            
            query = """
                SELECT TOP (?) timestamp, user_query, final_response, query_intent
                FROM chat_history 
                WHERE session_id = ? 
                ORDER BY timestamp DESC
            """
            
            df = pd.read_sql_query(query, conn, params=[limit, session_id])
            conn.close()
            
            if df.empty:
                return []
            
            messages = []
            # Reverse to get chronological order
            for _, row in reversed(list(df.iterrows())):
                # Add user message
                messages.append(ChatMessageContent(
                    role=AuthorRole.USER,
                    items=[TextContent(text=row['user_query'])]
                ))
                
                # Add assistant message
                messages.append(ChatMessageContent(
                    role=AuthorRole.ASSISTANT,
                    items=[TextContent(text=row['final_response'])]
                ))
            
            return messages
            
        except Exception as e:
            print(f"Error retrieving chat history: {str(e)}")
            return []
    
    async def remove_messages(self, session_id: str) -> bool:
        """Remove all messages for a session"""
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error removing messages: {str(e)}")
            return False
        
    async def get_session_token_stats(self, session_id: str) -> dict:
        """Get token usage statistics for a session"""
        try:
            conn = pyodbc.connect(self.connection_string)
            
            query = """
                SELECT 
                    COUNT(*) as total_messages,
                    SUM(token_count) as total_tokens,
                    SUM(token_price) as total_price_units,
                    AVG(token_count) as avg_tokens_per_message,
                    MAX(token_count) as max_tokens_single_message,
                    MIN(timestamp) as first_message,
                    MAX(timestamp) as last_message
                FROM chat_history 
                WHERE session_id = ? AND token_count IS NOT NULL
            """
            
            df = pd.read_sql_query(query, conn, params=[session_id])
            conn.close()
            
            if df.empty or df.iloc[0]['total_messages'] == 0:
                return {
                    'total_messages': 0,
                    'total_tokens': 0,
                    'total_cost': 0.0,
                    'avg_tokens_per_message': 0,
                    'max_tokens_single_message': 0,
                    'session_duration_minutes': 0
                }
            
            row = df.iloc[0]
            
            # Calculate session duration
            if row['first_message'] and row['last_message']:
                duration = (row['last_message'] - row['first_message']).total_seconds() / 60
            else:
                duration = 0
            
            return {
                'total_messages': int(row['total_messages']) if row['total_messages'] else 0,
                'total_tokens': int(row['total_tokens']) if row['total_tokens'] else 0,
                'total_cost': float(row['total_price_units'] / 10000) if row['total_price_units'] else 0.0,
                'avg_tokens_per_message': float(row['avg_tokens_per_message']) if row['avg_tokens_per_message'] else 0.0,
                'max_tokens_single_message': int(row['max_tokens_single_message']) if row['max_tokens_single_message'] else 0,
                'session_duration_minutes': duration
            }
            
        except Exception as e:
            print(f"Error getting token stats: {str(e)}")
            return {'error': str(e)}
    
    async def get_user_token_stats(self, user_id: str, days: int = 30) -> dict:
        """Get token usage statistics for a user over specified days"""
        try:
            conn = pyodbc.connect(self.connection_string)
            
            query = """
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT session_id) as total_sessions,
                    SUM(token_count) as total_tokens,
                    SUM(token_price) as total_price_units,
                    AVG(token_count) as avg_tokens_per_message
                FROM chat_history 
                WHERE user_id = ? 
                AND timestamp >= DATEADD(day, -?, GETDATE())
                AND token_count IS NOT NULL
            """
            
            df = pd.read_sql_query(query, conn, params=[user_id, days])
            conn.close()
            
            if df.empty or df.iloc[0]['total_messages'] == 0:
                return {
                    'total_messages': 0,
                    'total_sessions': 0,
                    'total_tokens': 0,
                    'total_cost': 0.0,
                    'avg_tokens_per_message': 0.0
                }
            
            row = df.iloc[0]
            
            return {
                'total_messages': int(row['total_messages']) if row['total_messages'] else 0,
                'total_sessions': int(row['total_sessions']) if row['total_sessions'] else 0,
                'total_tokens': int(row['total_tokens']) if row['total_tokens'] else 0,
                'total_cost': float(row['total_price_units'] / 10000) if row['total_price_units'] else 0.0,
                'avg_tokens_per_message': float(row['avg_tokens_per_message']) if row['avg_tokens_per_message'] else 0.0
            }
            
        except Exception as e:
            print(f"Error getting user token stats: {str(e)}")
            return {'error': str(e)}
