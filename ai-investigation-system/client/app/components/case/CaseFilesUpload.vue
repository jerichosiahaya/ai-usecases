<script setup lang="ts">
import { ref, computed } from 'vue'

const value = ref<File[]>([])
const loading = ref(false)
const message = ref<string | null>(null)
const error = ref<string | null>(null)

// Emit event so parent can handle uploading if desired
const emit = defineEmits<{ (e: 'submit', files: File[]): void }>()

// Validation rules
const MAX_FILES = 5
const MAX_SIZE_BYTES = 2 * 1024 * 1024 // 2MB

const hasFiles = computed(() => (value.value && value.value.length > 0))

function validateFiles(files: File[]) {
    if (!files?.length) return 'No files selected.'
    if (files.length > MAX_FILES) return `Select at most ${MAX_FILES} files.`
    for (const f of files) {
        if (f.size > MAX_SIZE_BYTES) return `File ${f.name} is larger than 2MB.`
    }
    return null
}

async function submitFiles() {
    message.value = null
    error.value = null
    const files = value.value ?? []
    const validation = validateFiles(files)
    if (validation) {
        error.value = validation
        return
    }

    // Let parent know about submit intent
    emit('submit', files)

    // Try to POST to an API endpoint if available. This is optional; parent can also handle upload.
    loading.value = true
    try {
        const form = new FormData()
        files.forEach((f) => form.append('files', f))

        // Prefer Nuxt's $fetch when available, fallback to window.fetch
        // @ts-ignore - $fetch is provided by Nuxt runtime when present
        if (typeof $fetch === 'function') {
            await $fetch('/api/files', { method: 'POST', body: form })
        } else {
            const resp = await fetch('/api/files', { method: 'POST', body: form })
            if (!resp.ok) throw new Error(await resp.text())
        }

        message.value = 'Files submitted successfully.'
        // clear selected files after successful submit
        value.value = []
    } catch (e: any) {
        error.value = e?.message ?? String(e)
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div>
        <UFileUpload v-model="value" icon="i-lucide-file" label="Drop your files here"
            description="PDF, DOCX, TXT, IMG (max. 2MB)" layout="list" multiple :interactive="false"
            class="w-full min-h-48">

            <template #actions="{ open }">
                <div class="flex gap-2 items-center">
                    <UButton label="Select files" icon="i-lucide-upload" color="neutral" variant="outline"
                        @click="open()" />
                </div>
            </template>

            <template #files-bottom="{ removeFile, files }">
                <div class="flex gap-2 items-center">
                    <UButton v-if="files?.length" label="Remove all files" color="neutral" @click="removeFile()" />
                    <UButton v-if="files?.length" :label="loading ? 'Uploading...' : 'Upload'" color="primary" :disabled="loading" @click="submitFiles" />
                </div>
            </template>

        </UFileUpload>

        <div class="mt-2">
            <P v-if="message" class="text-success">{{ message }}</P>
            <P v-if="error" class="text-danger">{{ error }}</P>
        </div>
    </div>
</template>
