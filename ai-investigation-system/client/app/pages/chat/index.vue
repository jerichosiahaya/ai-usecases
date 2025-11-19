<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { breakpointsTailwind } from '@vueuse/core'
import type { ChatHistory, FraudCase } from '~/types'
import { chatService } from '~/services/chatService'

const tabItems = [{
  label: 'All',
  value: 'all'
}, {
  label: 'Recent',
  value: 'recent'
}]
const selectedTab = ref('all')

// Load chat histories from localStorage
const chatHistories = ref<ChatHistory[]>([])
const { data: cases, pending: casesLoading } = await useFetch<FraudCase[]>('/api/cases', { default: () => [] })

// Load histories on mount
const loadChatHistories = () => {
  chatHistories.value = chatService.getAllSessions()
}

onMounted(() => {
  loadChatHistories()
})

// Filter chat histories based on the selected tab
const filteredChatHistories = computed(() => {
  if (selectedTab.value === 'recent') {
    const now = new Date()
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    return chatHistories.value.filter(chat => new Date(chat.updatedAt) > sevenDaysAgo)
  }

  return chatHistories.value
})

const selectedChat = ref<ChatHistory | null>()

const isChatPanelOpen = computed({
  get() {
    return !!selectedChat.value
  },
  set(value: boolean) {
    if (!value) {
      selectedChat.value = null
    }
  }
})

// Reset selected chat if it's not in the filtered chats
watch(filteredChatHistories, () => {
  if (!filteredChatHistories.value.find(chat => chat.id === selectedChat.value?.id)) {
    selectedChat.value = null
  }
})

const breakpoints = useBreakpoints(breakpointsTailwind)
const isMobile = breakpoints.smaller('lg')

const handleSelectCase = (caseId: string) => {
  const selectedCase = cases.value.find(c => c.id === caseId)
  if (selectedCase) {
    // Generate a session ID
    const sessionId = chatService.generateSessionId()
    
    // Create a new chat session
    chatService.createSession(selectedCase.id, sessionId, selectedCase.name)
    
    // Reload chat histories
    loadChatHistories()
    
    // Navigate to the chat details page
    navigateTo(`/chat/${selectedCase.id}/${sessionId}`)
  }
}

// Handle clicking on a chat from history
const handleSelectChatFromHistory = (chat: ChatHistory) => {
  navigateTo(`/chat/${chat.caseId}/${chat.id}`)
}

// Check for case selected from cases page
const checkSessionStorage = () => {
  if (typeof window === 'undefined') return
  
  const selectedCaseId = sessionStorage.getItem('selectedCaseId')
  
  if (selectedCaseId) {
    // Find the case in available cases
    const caseToSelect = cases.value.find(c => c.id === selectedCaseId)
    
    if (caseToSelect) {
      handleSelectCase(selectedCaseId)
    }
    
    // Clear session storage
    sessionStorage.removeItem('selectedCaseId')
    sessionStorage.removeItem('selectedCaseName')
    sessionStorage.removeItem('selectedCaseDescription')
    sessionStorage.removeItem('selectedCaseStatus')
  }
}

// Watch for cases to be loaded, then check session storage
watch(() => cases.value.length, () => {
  if (cases.value.length > 0) {
    checkSessionStorage()
  }
}, { immediate: true })
</script>

<template>
  <UDashboardPanel
    id="chat-1"
    :default-size="25"
    :min-size="20"
    :max-size="30"
    resizable
  >
    <UDashboardNavbar title="Chat">
      <template #leading>
        <UDashboardSidebarCollapse />
      </template>
      <template #trailing>
        <UBadge :label="filteredChatHistories.length" variant="subtle" />
      </template>

      <template #right>
        <UTabs
          v-model="selectedTab"
          :items="tabItems"
          :content="false"
          size="xs"
        />
      </template>
    </UDashboardNavbar>
    <ChatList 
      v-model="selectedChat" 
      :chats="filteredChatHistories"
      @delete="loadChatHistories"
      @chat_selected="handleSelectChatFromHistory"
    />
  </UDashboardPanel>

  <!-- Case Selector -->
  <div class="flex flex-1">
    <CaseSelector
      :cases="cases"
      :loading="casesLoading"
      @select="handleSelectCase"
    />
  </div>
</template>
