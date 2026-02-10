<script setup lang="ts">
import { ref } from 'vue'
import { columns } from '@/components/candidates/components/columns'
import DataTable from '@/components/candidates/components/DataTable.vue'
import type { Candidate } from '@/components/candidates/data/schema'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Plus, Upload, FileText, X } from 'lucide-vue-next'

const { data: candidates, pending: loading, error, refresh } = await useFetch<Candidate[]>('/api/candidates')

const isUploadDialogOpen = ref(false)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

const removeFile = () => {
  selectedFile.value = null
}

const handleUpload = async () => {
  if (!selectedFile.value) return
  
  isUploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('cv', selectedFile.value)

    await $fetch('/api/candidates/create-from-cv', {
      method: 'POST',
      body: formData
    })
    
    // Close dialog and refresh list
    isUploadDialogOpen.value = false
    selectedFile.value = null
    refresh()
  } catch (e) {
    console.error('Error uploading candidate:', e)
  } finally {
    isUploading.value = false
  }
}

console.log('Candidates data:', candidates)
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-3xl font-bold tracking-tight">
          Applicants
        </h2>
        <p class="text-muted-foreground mt-1">
          Manage and review applicant applications and profiles
        </p>
      </div>
      <Button @click="isUploadDialogOpen = true" class="gap-2">
        <Plus class="h-4 w-4" />
        Add Applicant
      </Button>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>

    <!-- Candidates Table -->
    <DataTable v-if="!loading && !error && candidates" :data="candidates" :columns="columns" />

    <!-- Upload Dialog -->
    <Dialog :open="isUploadDialogOpen" @update:open="isUploadDialogOpen = $event">
      <DialogContent class="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add New Candidate</DialogTitle>
          <DialogDescription>
            Upload a candidate's CV (PDF) to automatically extract their information and add them to the database.
          </DialogDescription>
        </DialogHeader>
        
        <div class="grid gap-4 py-4">
          <div 
            class="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors"
            :class="selectedFile ? 'border-primary/50 bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/5'"
            @dragover.prevent
            @drop="handleDrop"
            @click="$refs.fileInput.click()"
          >
            <input 
              ref="fileInput"
              type="file" 
              class="hidden" 
              accept=".pdf,.doc,.docx" 
              @change="handleFileChange"
            />
            
            <div v-if="selectedFile" class="flex flex-col items-center gap-2">
              <div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <FileText class="h-6 w-6" />
              </div>
              <div class="font-medium text-sm">{{ selectedFile.name }}</div>
              <div class="text-xs text-muted-foreground">{{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</div>
              <Button variant="ghost" size="sm" class="mt-2 h-8 text-red-500 hover:text-red-600 hover:bg-red-50" @click.stop="removeFile">
                Remove file
              </Button>
            </div>
            
            <div v-else class="flex flex-col items-center gap-2">
              <div class="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                <Upload class="h-6 w-6 text-muted-foreground" />
              </div>
              <div class="font-medium">Click to upload or drag and drop</div>
              <div class="text-xs text-muted-foreground">PDF, DOC, DOCX up to 10MB</div>
            </div>
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" @click="isUploadDialogOpen = false" :disabled="isUploading">
            Cancel
          </Button>
          <Button @click="handleUpload" :disabled="!selectedFile || isUploading" class="gap-2">
            <div v-if="isUploading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            <Upload v-else class="h-4 w-4" />
            {{ isUploading ? 'Processing...' : 'Upload & Extract' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>