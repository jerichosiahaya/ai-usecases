<script setup lang="ts">
import { computed, ref, watch, nextTick, onMounted } from 'vue'
import type { ChatMessage, FraudCase } from '~/types'
import { chatService } from '~/services/chatService'
import { caseService } from '~/services/caseService'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const caseId = route.params.caseId as string
const sessionId = route.params.sessionId as string

// State
const fraudCase = ref<FraudCase | null>(null)
const chatMessages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const loading = ref(false)
const casesLoading = ref(false)
const messagesEndRef = ref<HTMLDivElement>()

// Get or create chat session
const chatSession = computed(() => {
  return chatService.getSession(sessionId)
})

// Fetch case details
const fetchCase = async () => {
  try {
    casesLoading.value = true
    fraudCase.value = await caseService.getCaseById(caseId)
    
    // If session doesn't exist, create it
    if (!chatSession.value && fraudCase.value) {
      chatService.createSession(caseId, sessionId, fraudCase.value.name)
    }
  } catch (error) {
    console.error('Error loading case:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to load case details',
      color: 'error'
    })
    // Don't redirect on error, just show the session data
  } finally {
    casesLoading.value = false
  }
}

// Load initial messages
const loadMessages = () => {
  const messages = chatService.getChatHistory(sessionId)
  chatMessages.value = [...messages] // Create a copy to avoid reference issues
}

// Initialize on mount
onMounted(async () => {
  console.log('Chat page mounted - caseId:', caseId, 'sessionId:', sessionId)
  
  // First check if session already exists in service
  const existingSession = chatService.getSession(sessionId)
  console.log('Existing session:', existingSession)
  
  await fetchCase()
  loadMessages()
  
  console.log('Chat messages loaded:', chatMessages.value.length)
})

// Auto-scroll to bottom
const scrollToBottom = () => {
  nextTick(() => {
    messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

// Watch for new messages
watch(() => chatMessages.value.length, () => {
  scrollToBottom()
})

// Send message handler
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  try {
    loading.value = true
    inputMessage.value = ''

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }
    chatMessages.value.push(userMessage)

    // Ensure loading indicator is shown for at least 500ms
    const startTime = Date.now()
    
    // Send to backend
    const response = await chatService.sendMessage(caseId, sessionId, message)

    // Calculate elapsed time and add minimum delay if needed
    const elapsedTime = Date.now() - startTime
    const minimumLoadingTime = 500 // Show loading for at least 500ms
    if (elapsedTime < minimumLoadingTime) {
      await new Promise(resolve => setTimeout(resolve, minimumLoadingTime - elapsedTime))
    }

    // Add assistant message to UI
    const assistantMessage: ChatMessage = {
      id: `msg-${Date.now() + 1}`,
      role: 'assistant',
      content: response.assistantMessage,
      timestamp: new Date().toISOString()
    }
    chatMessages.value.push(assistantMessage)

  } catch (error) {
    console.error('Error sending message:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to send message',
      color: 'error'
    })
    // Remove user message if there was an error
    chatMessages.value.pop()
  } finally {
    loading.value = false
  }
}

// Handle Enter key
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// Format timestamp
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

// Parse markdown to HTML using marked library
const parseMarkdown = (text: string): string => {
  try {
    // Configure marked for better rendering
    marked.setOptions({
      breaks: true,
      gfm: true, // GitHub Flavored Markdown (enables tables)
    })
    return marked(text) as string
  } catch (error) {
    console.error('Error parsing markdown:', error)
    return `<p>${text}</p>`
  }
}
</script>

<template>
  <div class="flex h-screen flex-col bg-elevated">
    <!-- Header -->
    <div class="border-b border-default bg-elevated px-6 py-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <UButton
            icon="i-lucide-arrow-left"
            color="neutral"
            variant="ghost"
            @click="router.push('/chat')"
          />
          <div>
            <h1 class="text-lg font-semibold">
              {{ fraudCase?.name || chatSession?.caseName || 'Chat Session' }}
            </h1>
            <p class="text-xs text-muted">Session: {{ sessionId }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <UBadge
            v-if="fraudCase"
            :color="{ pending: 'warning', analyzing: 'info', completed: 'success', archived: 'neutral' }[fraudCase.status] as any"
            variant="soft"
            class="capitalize"
          >
            {{ fraudCase.status }}
          </UBadge>
          <UButton
            icon="i-lucide-x"
            color="neutral"
            variant="ghost"
            @click="router.push('/chat')"
          />
        </div>
      </div>
    </div>

    <!-- Case Context Card -->
    <div v-if="fraudCase || chatSession" class="border-b border-default bg-elevated px-6 py-3">
      <div class="rounded-lg bg-elevated/50 p-3 text-sm">
        <p class="mb-1 font-medium text-highlighted">Case Context:</p>
        <p class="line-clamp-2 text-muted">{{ fraudCase?.description || 'No description available' }}</p>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4">
      <!-- Empty state -->
      <div v-if="chatMessages.length === 0" class="flex h-full items-center justify-center">
        <div class="text-center">
          <UIcon name="i-lucide-message-circle" class="w-12 h-12 text-muted mx-auto mb-3" />
          <p class="text-muted mb-1">No messages yet</p>
          <p class="text-xs text-muted/60 max-w-xs">
            Start a conversation with the AI analyst. Ask questions about the case, request analysis, or seek recommendations.
          </p>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="message in chatMessages" :key="message.id" class="flex gap-3">
        <!-- User message -->
        <div v-if="message.role === 'user'" class="flex justify-end w-full">
          <div class="max-w-md lg:max-w-lg rounded-lg bg-primary/10 border border-primary/20 p-3">
            <p class="text-sm wrap-break-word">{{ message.content }}</p>
            <p class="text-xs text-muted mt-1">{{ formatTime(message.timestamp) }}</p>
          </div>
        </div>

        <!-- Assistant message -->
        <div v-else class="flex gap-3 max-w-2xl">
          <div class="h-8 w-8 rounded-full bg-success/20 flex items-center justify-center shrink-0 mt-1">
            <UIcon name="i-lucide-bot" class="w-4 h-4 text-success" />
          </div>
          <div class="rounded-lg bg-elevated border border-default p-4 flex-1">
            <div class="prose prose-sm max-w-none dark:prose-invert text-sm leading-relaxed" v-html="parseMarkdown(message.content)"></div>
            <p class="text-xs text-muted mt-3">{{ formatTime(message.timestamp) }}</p>
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="flex gap-3 animate-in fade-in duration-300">
        <div class="h-8 w-8 rounded-full bg-success/20 flex items-center justify-center shrink-0">
          <UIcon name="i-lucide-bot" class="w-4 h-4 text-success" />
        </div>
        <div class="rounded-lg bg-success/5 border border-success/20 p-4 min-w-[100px]">
          <div class="flex gap-2 items-center justify-center">
            <div class="w-2 h-2 rounded-full bg-success/60 animate-bounce" style="animation-delay: 0s;"></div>
            <div class="w-2 h-2 rounded-full bg-success/60 animate-bounce" style="animation-delay: 0.15s;"></div>
            <div class="w-2 h-2 rounded-full bg-success/60 animate-bounce" style="animation-delay: 0.3s;"></div>
          </div>
        </div>
      </div>

      <!-- Scroll anchor -->
      <div ref="messagesEndRef" />
    </div>

    <!-- Input Area -->
    <div class="border-t border-default bg-elevated px-6 py-4">
      <div class="flex gap-2">
        <div class="flex-1">
          <UTextarea
            v-model="inputMessage"
            placeholder="Ask me anything about this case..."
            :rows="3"
            :disabled="loading || casesLoading"
            @keydown="handleKeyDown"
            class="w-full"
          />
        </div>
        <UButton
          icon="i-lucide-send"
          color="primary"
          :loading="loading"
          :disabled="!inputMessage.trim() || loading || casesLoading"
          @click="sendMessage"
          class="self-end mb-1"
        />
      </div>
      <p class="text-xs text-muted mt-2">Press Enter to send, Shift+Enter for new line</p>
    </div>
  </div>
</template>

<style scoped>
:deep(.prose) {
  --tw-prose-body: currentColor;
  --tw-prose-headings: currentColor;
  --tw-prose-lead: currentColor;
  --tw-prose-links: currentColor;
  --tw-prose-bold: currentColor;
  --tw-prose-counters: currentColor;
  --tw-prose-bullets: currentColor;
  --tw-prose-hr: currentColor;
  --tw-prose-quotes: currentColor;
  --tw-prose-quote-borders: currentColor;
  --tw-prose-captions: currentColor;
  --tw-prose-code: currentColor;
  --tw-prose-pre-bg: currentColor;
  --tw-prose-pre-border: currentColor;
  --tw-prose-pre-code: currentColor;
  --tw-prose-thead-bg: currentColor;
  --tw-prose-thead-borders: currentColor;
  --tw-prose-tbody-tr-borders: currentColor;
}

:deep(h1) {
  font-size: 1.875rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

:deep(h2) {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}

:deep(h3) {
  font-size: 1.125rem;
  font-weight: 700;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}

:deep(p) {
  margin-bottom: 0.5rem;
}

:deep(ul) {
  list-style-type: disc;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
}

:deep(li) {
  margin-left: 0;
  margin-bottom: 0.25rem;
}

:deep(strong) {
  font-weight: 700;
}

:deep(em) {
  font-style: italic;
}

:deep(code) {
  background-color: rgb(229 229 229);
  padding: 0.375rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, monospace;
}

:deep(.dark) code {
  background-color: rgb(31 41 55);
}

:deep(pre) {
  background-color: rgb(17 24 39);
  color: rgb(243 244 246);
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, monospace;
}

:deep(pre) code {
  background-color: transparent;
  padding: 0;
}

:deep(blockquote) {
  border-left: 4px solid rgb(59 130 246);
  padding-left: 1rem;
  font-style: italic;
  color: rgb(107 114 128);
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

/* Table styles - Dark background by default */
:deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  border: 1px solid rgb(55 65 81);
  border-radius: 0.375rem;
  overflow: hidden;
}

:deep(thead) {
  background-color: rgb(31 41 55);
}

:deep(tbody) {
  background-color: rgb(17 24 39);
}

:deep(th) {
  background-color: rgb(31 41 55);
  padding: 0.75rem;
  text-align: left;
  font-weight: 700;
  border-right: 1px solid rgb(55 65 81);
  border-bottom: 2px solid rgb(75 85 99);
  color: rgb(243 244 246);
}

:deep(th:last-child) {
  border-right: none;
}

:deep(td) {
  padding: 0.75rem;
  border-right: 1px solid rgb(55 65 81);
  border-bottom: 1px solid rgb(55 65 81);
  color: rgb(209 213 219);
}

:deep(td:last-child) {
  border-right: none;
}

:deep(tbody tr:last-child td) {
  border-bottom: none;
}

:deep(tbody tr:hover) {
  background-color: rgb(31 41 55);
}

</style>
