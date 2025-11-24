<script setup lang="ts">
import { format } from 'date-fns'
import type { ChatHistory, ChatMessage, FraudCase } from '~/types'

const props = defineProps<{
  chat: ChatHistory
  caseInfo?: FraudCase
}>()

const emits = defineEmits(['close'])

const dropdownItems = [[{
  label: 'Rename',
  icon: 'i-lucide-edit'
}, {
  label: 'Export',
  icon: 'i-lucide-download'
}], [{
  label: 'Delete',
  icon: 'i-lucide-trash-2'
}]]

const toast = useToast()

const message = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement>()

// Simulated messages state (in real app, would be synced with chat.messages)
const messages = ref<ChatMessage[]>([])

onMounted(() => {
  messages.value = props.chat.messages
})

function onSubmit() {
  if (!message.value.trim()) {
    return
  }

  loading.value = true

  // Add user message
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: message.value,
    timestamp: new Date().toISOString()
  }
  messages.value.push(userMessage)

  // Simulate assistant response with RAG context
  setTimeout(() => {
    const ragContext = props.caseInfo
      ? `\n\n[RAG Context from Case: ${props.caseInfo.name}]\nStatus: ${props.caseInfo.status}\nDescription: ${props.caseInfo.description}`
      : ''

    const assistantMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `I'm analyzing your question based on the case context. Your question: "${message.value}"${ragContext}\n\nI'll provide a detailed analysis considering the case information above.`,
      timestamp: new Date().toISOString()
    }
    messages.value.push(assistantMessage)

    message.value = ''
    loading.value = false

    // Scroll to bottom
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  }, 1000)
}

watch(messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})
</script>

<template>
  <UDashboardPanel id="chat-2" class="flex flex-col">
    <UDashboardNavbar :title="chat.title" :toggle="false" class="shrink-0">
      <template #leading>
        <UButton
          icon="i-lucide-x"
          color="neutral"
          variant="ghost"
          class="-ms-1.5"
          @click="emits('close')"
        />
      </template>

      <template #right>
        <UTooltip v-if="caseInfo" :text="`Case: ${caseInfo.name}`">
          <UButton
            icon="i-lucide-briefcase"
            color="neutral"
            variant="ghost"
          />
        </UTooltip>

        <UDropdownMenu :items="dropdownItems">
          <UButton
            icon="i-lucide-ellipsis-vertical"
            color="neutral"
            variant="ghost"
          />
        </UDropdownMenu>
      </template>
    </UDashboardNavbar>

    <!-- Case Context -->
    <div v-if="caseInfo" class="shrink-0 border-b border-default bg-primary/5 p-4 sm:p-6">
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1">
          <h3 class="font-semibold text-highlighted mb-1">
            {{ caseInfo.name }}
          </h3>
          <p class="text-sm text-dimmed mb-2">
            {{ caseInfo.description }}
          </p>
          <div class="flex items-center gap-4 text-xs text-muted">
            <span>ID: {{ caseInfo.id }}</span>
            <UBadge :label="caseInfo.status" variant="subtle" class="capitalize" />
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-col flex-1 min-h-0">
      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        <div v-if="messages.length === 0" class="flex items-center justify-center h-full text-dimmed">
          <div class="text-center">
            <UIcon name="i-lucide-message-circle" class="size-12 mx-auto mb-2" />
            <p class="text-sm">Start analyzing this case with AI assistance</p>
            <p class="text-xs text-muted mt-1">Ask questions about the case to get insights</p>
          </div>
        </div>

        <div v-for="msg in messages" :key="msg.id" class="flex gap-3" :class="[msg.role === 'assistant' && 'flex-row-reverse']">
          <!-- Avatar -->
          <div class="shrink-0">
            <UAvatar
              :src="msg.role === 'assistant' ? 'https://api.dicebear.com/7.x/avataaars/svg?seed=bot' : 'https://api.dicebear.com/7.x/avataaars/svg?seed=user'"
              :alt="msg.role"
              size="sm"
            />
          </div>

          <!-- Message -->
          <div class="flex flex-col gap-1" :class="[msg.role === 'assistant' ? 'items-start' : 'items-end']">
            <div
              class="max-w-xs lg:max-w-md px-3 py-2 rounded-lg"
              :class="[
                msg.role === 'assistant'
                  ? 'bg-gray-100 dark:bg-gray-900 text-highlighted'
                  : 'bg-primary text-white'
              ]"
            >
              <p class="whitespace-pre-wrap wrap-break-word text-sm">
                {{ msg.content }}
              </p>
            </div>
            <span class="text-xs text-dimmed">
              {{ format(new Date(msg.timestamp), 'HH:mm') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="pb-4 px-4 sm:px-6 shrink-0 border-t border-default">
        <form @submit.prevent="onSubmit" class="mt-4">
          <div class="flex items-end gap-2">
            <UTextarea
              v-model="message"
              color="neutral"
              variant="subtle"
              placeholder="Type your message..."
              :rows="1"
              :disabled="loading"
              autoresize
              class="w-full"
              :ui="{ base: 'resize-none' }"
            />

            <UButton
              type="submit"
              :loading="loading"
              icon="i-lucide-send"
              color="primary"
              variant="solid"
              size="md"
              :disabled="!message.trim()"
              class="shrink-0"
            />
          </div>
        </form>
      </div>
    </div>
  </UDashboardPanel>
</template>
