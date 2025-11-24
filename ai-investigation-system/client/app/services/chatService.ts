import type { ChatMessage, ChatHistory } from '~/types'

const API_BASE_URL = 'https://ai-investigation-server.azurewebsites.net/api/v1'

interface ApiResponse<T> {
  status: string
  message: string
  data: T
}

interface ChatRequest {
  messages: ChatMessage[]
  session_id?: string
}

interface ChatResponse {
  response: string
  source_references?: string[]
  visualization?: boolean
}

// In-memory storage for chat sessions (with localStorage persistence)
const chatSessions: Map<string, ChatHistory> = new Map()
const STORAGE_KEY = 'ai_fraud_chat_sessions'

// Load sessions from localStorage on initialization
const loadSessionsFromStorage = () => {
  if (typeof window === 'undefined') return
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const sessions = JSON.parse(stored)
      Object.entries(sessions).forEach(([sessionId, session]: [string, any]) => {
        chatSessions.set(sessionId, session)
      })
    }
  } catch (error) {
    console.error('Error loading sessions from localStorage:', error)
  }
}

// Save sessions to localStorage
const saveSessionsToStorage = () => {
  if (typeof window === 'undefined') return
  
  try {
    const sessions: Record<string, ChatHistory> = {}
    chatSessions.forEach((session, sessionId) => {
      sessions[sessionId] = session
    })
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
  } catch (error) {
    console.error('Error saving sessions to localStorage:', error)
  }
}

// Initialize storage on module load
loadSessionsFromStorage()

export const chatService = {
  // Create a new chat session
  createSession(caseId: string, sessionId: string, caseName: string): ChatHistory {
    const session: ChatHistory = {
      id: sessionId,
      caseId,
      caseName,
      title: `Chat: ${caseName}`,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    chatSessions.set(sessionId, session)
    saveSessionsToStorage()
    return session
  },

  // Get existing chat session
  getSession(sessionId: string): ChatHistory | undefined {
    return chatSessions.get(sessionId)
  },

  // Get all sessions for a case
  getSessionsByCase(caseId: string): ChatHistory[] {
    return Array.from(chatSessions.values()).filter(session => session.caseId === caseId)
  },

  // Send a message and get response from backend API
  async sendMessage(
    caseId: string,
    sessionId: string,
    userMessage: string
  ): Promise<{ assistantMessage: string; sourceReferences?: string[] }> {
    try {
      // Get existing session to include message history
      const session = this.getSession(sessionId)
      if (!session) {
        throw new Error('Session not found')
      }

      // Build messages array for API (only send recent context to avoid token limits)
      const recentMessages = session.messages.slice(-10) // Keep last 10 messages
      
      // Transform messages to backend format: 'content' -> 'text'
      const messagesForApi = [
        ...recentMessages.map(msg => ({
          role: msg.role,
          text: msg.content
        })),
        {
          role: 'user' as const,
          text: userMessage
        }
      ]

      // Call backend API
      const response = await $fetch<ApiResponse<ChatResponse>>(
        `${API_BASE_URL}/cases/${caseId}/chat`,
        {
          method: 'POST',
          body: {
            messages: messagesForApi,
            session_id: sessionId,
            case_id: caseId
          }
        }
      )

      const assistantMessage = response.data.response
      const sourceReferences = response.data.source_references || []

      // Add messages to session for persistence
      // User message
      session.messages.push({
        id: `msg-${Date.now()}`,
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      })

      // Assistant message
      session.messages.push({
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: assistantMessage,
        timestamp: new Date().toISOString()
      })

      // Update session timestamp
      session.updatedAt = new Date().toISOString()

      // Persist session (in real app, this would save to database)
      chatSessions.set(sessionId, session)
      saveSessionsToStorage()

      return {
        assistantMessage,
        sourceReferences
      }
    } catch (error) {
      console.error('Error sending message:', error)
      throw error
    }
  },

  // Add message to session locally (for UI updates)
  addMessageToSession(sessionId: string, message: ChatMessage): void {
    const session = chatSessions.get(sessionId)
    if (session) {
      session.messages.push(message)
      session.updatedAt = new Date().toISOString()
      chatSessions.set(sessionId, session)
    }
  },

  // Get chat history
  getChatHistory(sessionId: string): ChatMessage[] {
    const session = chatSessions.get(sessionId)
    return session?.messages || []
  },

  // Clear chat session
  clearSession(sessionId: string): void {
    chatSessions.delete(sessionId)
    saveSessionsToStorage()
  },

  // Get all sessions
  getAllSessions(): ChatHistory[] {
    return Array.from(chatSessions.values()).sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  },

  // Generate a unique session ID
  generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }
}
