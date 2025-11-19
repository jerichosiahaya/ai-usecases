<script setup lang="ts">
import { format, isToday } from 'date-fns'
import type { ChatHistory } from '~/types'
import { chatService } from '~/services/chatService'

const props = defineProps<{
  chats: ChatHistory[]
}>()

const emit = defineEmits<{
  delete: [chatId: string]
  chat_selected: [chat: ChatHistory]
}>()

const chatsRefs = ref<Record<string, Element>>({})

const selectedChat = defineModel<ChatHistory | null>()

watch(selectedChat, () => {
  if (!selectedChat.value) {
    return
  }
  const ref = chatsRefs.value[selectedChat.value.id]
  if (ref) {
    ref.scrollIntoView({ block: 'nearest' })
  }
  // Emit event when chat is selected
  emit('chat_selected', selectedChat.value)
})

const handleDeleteChat = (chatId: string, event: Event) => {
  event.stopPropagation()
  chatService.clearSession(chatId)
  if (selectedChat.value?.id === chatId) {
    selectedChat.value = null
  }
  emit('delete', chatId)
}

defineShortcuts({
  arrowdown: () => {
    const index = props.chats.findIndex(chat => chat.id === selectedChat.value?.id)

    if (index === -1) {
      selectedChat.value = props.chats[0]
    } else if (index < props.chats.length - 1) {
      selectedChat.value = props.chats[index + 1]
    }
  },
  arrowup: () => {
    const index = props.chats.findIndex(chat => chat.id === selectedChat.value?.id)

    if (index === -1) {
      selectedChat.value = props.chats[props.chats.length - 1]
    } else if (index > 0) {
      selectedChat.value = props.chats[index - 1]
    }
  }
})
</script>

<template>
  <div class="overflow-y-auto divide-y divide-default">
    <div
      v-for="(chat, index) in chats"
      :key="index"
      :ref="el => { chatsRefs[chat.id] = el as Element }"
    >
      <div
        class="p-4 sm:px-6 text-sm cursor-pointer border-l-2 transition-colors group"
        :class="[
          selectedChat && selectedChat.id === chat.id
            ? 'border-primary bg-primary/10'
            : 'border-bg hover:border-primary hover:bg-primary/5'
        ]"
        @click="selectedChat = chat"
      >
        <div class="flex items-center justify-between mb-1">
          <p class="font-semibold text-highlighted truncate flex-1">
            {{ chat.title }}
          </p>
          <div class="flex items-center gap-2 ml-2">
            <span class="text-xs text-dimmed shrink-0">
              {{ isToday(new Date(chat.updatedAt)) ? format(new Date(chat.updatedAt), 'HH:mm') : format(new Date(chat.updatedAt), 'dd MMM') }}
            </span>
            <UButton
              icon="i-lucide-trash-2"
              color="neutral"
              variant="ghost"
              size="xs"
              class="opacity-0 group-hover:opacity-100 transition-opacity"
              @click="handleDeleteChat(chat.id, $event)"
            />
          </div>
        </div>

        <p class="text-xs text-muted truncate mb-2">
          📋 {{ chat.caseName }}
        </p>

        <p class="text-dimmed line-clamp-1 text-xs">
          {{ chat.messages[chat.messages.length - 1]?.content || 'No messages yet' }}
        </p>
      </div>
    </div>
  </div>
</template>
