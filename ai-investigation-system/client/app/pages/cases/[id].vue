<script setup lang="ts">
import type { FraudCase } from '~/types'
import { caseService } from '~/services/caseService'
import { chatService } from '~/services/chatService'
import { fileService } from '~/services/fileService'
import { marked } from 'marked'
import { reactive } from "vue"
import { defineConfigs, type Layouts, VNetworkGraph, VEdgeLabel } from 'v-network-graph'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const caseId = route.params.id as string
const fraudCase = ref<FraudCase | null>(null)
const loading = ref(true)
const showPendingAlert = ref(true)

const initialConfigs = defineConfigs({
  node: {
    selectable: true,
    label: {
      hoverable: true,
      visible: true,
      background: {
        visible: false,
        color: "#ffffff",
        padding: {
          vertical: 1,
          horizontal: 4,
        },
      }
    }
  },
  edge: {
    selectable: true,
    label: {
      hoverable: true,
      fontFamily: "monospace",
      fontSize: 8,
      lineHeight: 1.1,
      color: "#000000",
      margin: 4,
      background: {
        visible: true,
        color: "#ffffff",
        padding: {
          vertical: 1,
          horizontal: 4,
        },
      borderRadius: 2,
      },
    }
  }
})
const configs = reactive(initialConfigs)

const fetchCase = async () => {
  try {
    loading.value = true
    fraudCase.value = await caseService.getCaseById(caseId)
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to load case details',
      color: 'error'
    })
    router.push('/cases')
  } finally {
    loading.value = false
  }
}

await fetchCase()

const statusColor = computed(() => {
  const colorMap: Record<string, string> = {
    pending: 'warning',
    analyzing: 'info',
    completed: 'success',
    archived: 'neutral'
  }
  return colorMap[fraudCase.value?.status || 'pending']
})

const analyzeCase = async () => {
  if (!fraudCase.value) return
  try {
    loading.value = true
    await caseService.analyzeCase(fraudCase.value.id)
    fraudCase.value.status = 'analyzing'
    toast.add({
      title: 'Analysis Started',
      description: 'AI analysis has been initiated for this case',
      color: 'success'
    })
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to start analysis',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

const openChatAssistant = () => {
  if (!fraudCase.value) return
  
  // Generate a session ID
  const sessionId = chatService.generateSessionId()
  
  // Create a new chat session
  chatService.createSession(fraudCase.value.id, sessionId, fraudCase.value.name)
  
  // Navigate to the chat details page
  router.push(`/chat/${fraudCase.value.id}/${sessionId}`)
}

const onFileUploaded = async () => {
  // Refresh case data to get updated files list
  await fetchCase()
}

const onDeleteFile = async (fileName: string) => {
  if (!confirm('Are you sure you want to delete this file?')) return
  
  try {
    loading.value = true
    await fileService.deleteFile(caseId, fileName)
    toast.add({
      title: 'Success',
      description: 'File deleted successfully',
      color: 'success'
    })
    // Refresh case data to get updated files list
    await fetchCase()
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to delete file',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

const newNote = ref('')
const notesLoading = ref(false)

const addNote = async () => {
  if (!fraudCase.value || !newNote.value.trim()) return

  try {
    notesLoading.value = true
    await caseService.addNote(fraudCase.value.id, newNote.value)
    toast.add({
      title: 'Success',
      description: 'Note added successfully',
      color: 'success'
    })
    newNote.value = ''
    // Refresh case data to get updated notes
    await fetchCase()
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to add note',
      color: 'error'
    })
  } finally {
    notesLoading.value = false
  }
}

const deleteNote = async (noteId: string) => {
  if (!confirm('Are you sure you want to delete this note?')) return
  if (!fraudCase.value) return

  try {
    notesLoading.value = true
    await caseService.deleteNote(fraudCase.value.id, noteId)
    toast.add({
      title: 'Success',
      description: 'Note deleted successfully',
      color: 'success'
    })
    // Refresh case data to get updated notes
    await fetchCase()
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to delete note',
      color: 'error'
    })
  } finally {
    notesLoading.value = false
  }
}

// Parse markdown to HTML using marked library
const parseMarkdown = (text: string): string => {
  try {
    // Replace escaped newlines with actual newlines
    const processedText = text.replace(/\\n/g, '\n')
    
    // Configure marked for better rendering
    marked.setOptions({
      breaks: true,
      gfm: true, // GitHub Flavored Markdown (enables tables)
    })
    return marked(processedText) as string
  } catch (error) {
    console.error('Error parsing markdown:', error)
    return `<p>${text}</p>`
  }
}

// Knowledge Graph related computed properties
const graphData = computed(() => {
  if (!fraudCase.value?.knowledge_graph) {
    return { nodes: {}, edges: {} }
  }
  return fraudCase.value.knowledge_graph
})

const nodes = computed(() => {
  return graphData.value.nodes || {}
})

const edges = computed(() => {
  return graphData.value.edges || {}
})

const hasKnowledgeGraph = computed(() => {
  return Object.keys(nodes.value).length > 0
})

// Draggable node positions - stored as ref so they can be updated
const draggableNodePositions = ref<Record<string, { x: number; y: number }>>({})
const draggedNode = ref<string | null>(null)

// Auto layout for v-network-graph using force-directed layout
const vNetworkGraphLayouts = computed<Layouts>(() => {
  const nodeIds = Object.keys(nodes.value)
  if (nodeIds.length === 0) return { nodes: {} }

  const positions: Record<string, { x: number; y: number }> = {}

  // Initialize random positions
  nodeIds.forEach((nodeId) => {
    positions[nodeId] = {
      x: Math.random() * 400 - 200,
      y: Math.random() * 400 - 200,
    }
  })

  // Apply force-directed layout algorithm
  const iterations = 50
  const k = Math.sqrt(40000 / nodeIds.length)
  const c = 0.1

  for (let iter = 0; iter < iterations; iter++) {
    const forces: Record<string, { x: number; y: number }> = {}
    
    nodeIds.forEach((id) => {
      forces[id] = { x: 0, y: 0 }
    })

    // Repulsive forces between all node pairs
    for (let i = 0; i < nodeIds.length; i++) {
      for (let j = i + 1; j < nodeIds.length; j++) {
        const id1 = nodeIds[i]!
        const id2 = nodeIds[j]!
        const pos1 = positions[id1]
        const pos2 = positions[id2]
        if (!pos1 || !pos2) continue

        const dx = pos2.x - pos1.x
        const dy = pos2.y - pos1.y
        const distance = Math.sqrt(dx * dx + dy * dy) || 1
        const repulsion = (k * k) / distance
        
        forces[id1]!.x -= (dx / distance) * repulsion
        forces[id1]!.y -= (dy / distance) * repulsion
        forces[id2]!.x += (dx / distance) * repulsion
        forces[id2]!.y += (dy / distance) * repulsion
      }
    }

    // Attractive forces along edges
    Object.values(edges.value).forEach((edge: any) => {
      const srcPos = positions[edge.source]
      const tgtPos = positions[edge.target]
      if (!srcPos || !tgtPos) return

      const dx = tgtPos.x - srcPos.x
      const dy = tgtPos.y - srcPos.y
      const distance = Math.sqrt(dx * dx + dy * dy) || 1
      const attraction = (distance - k) / distance
      
      forces[edge.source]!.x += (dx / distance) * attraction * 0.5
      forces[edge.source]!.y += (dy / distance) * attraction * 0.5
      forces[edge.target]!.x -= (dx / distance) * attraction * 0.5
      forces[edge.target]!.y -= (dy / distance) * attraction * 0.5
    })

    // Update positions based on forces
    nodeIds.forEach((id) => {
      const force = forces[id]
      if (!force) return
      const fx = force.x
      const fy = force.y
      const distance = Math.sqrt(fx * fx + fy * fy)
      if (distance > 0) {
        const displacement = Math.min(distance, 5)
        positions[id]!.x += (fx / distance) * displacement * c
        positions[id]!.y += (fy / distance) * displacement * c
      }
    })
  }

  return { nodes: positions }
})

// Initialize positions when nodes change
watch(nodes, () => {
  const positions: Record<string, { x: number; y: number }> = {}
  const nodeIds = Object.keys(nodes.value)
  const radius = 150
  const centerX = 400
  const centerY = 250

  nodeIds.forEach((nodeId, index) => {
    const angle = (index / nodeIds.length) * 2 * Math.PI
    positions[nodeId] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    }
  })

  draggableNodePositions.value = positions
}, { immediate: true })

// Helper function to wrap text for SVG display
const wrapText = (text: string, maxCharsPerLine: number): string[] => {
  const words = text.split(' ')
  const lines: string[] = []
  let currentLine = ''

  for (const word of words) {
    if ((currentLine + word).length > maxCharsPerLine) {
      if (currentLine) lines.push(currentLine.trim())
      currentLine = word
    } else {
      currentLine += (currentLine ? ' ' : '') + word
    }
  }
  if (currentLine) lines.push(currentLine.trim())
  return lines
}

// Mouse event handlers for dragging
const handleNodeMouseDown = (nodeId: string, event: MouseEvent) => {
  draggedNode.value = nodeId
  event.preventDefault()
}

const handleSvgMouseMove = (event: MouseEvent) => {
  if (!draggedNode.value) return

  const svg = (event.target as SVGElement).closest('svg') as SVGSVGElement
  if (!svg) return

  const rect = svg.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  draggableNodePositions.value[draggedNode.value] = { x, y }
}

const handleSvgMouseUp = () => {
  draggedNode.value = null
}

const graphSvgWidth = computed(() => 800)
const graphSvgHeight = computed(() => 500)

// Helper function to get classification badge color
const getClassificationColor = (classification: string): 'error' | 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'neutral' => {
  const colorMap: Record<string, 'error' | 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'neutral'> = {
    'Chat': 'info',
    'Audit': 'primary',
    'Finance': 'success',
    'Memo': 'warning',
  }
  return colorMap[classification] || 'neutral'
}
</script>

<template>
  <UDashboardPanel v-if="fraudCase" id="case-detail">
    <template #header>
      <UDashboardNavbar :title="`Case: ${fraudCase.name}`">
        <template #leading>
          <UButton
            icon="i-lucide-arrow-left"
            color="neutral"
            variant="ghost"
            @click="router.push('/cases')"
          />
        </template>

        <template #right>
          <div class="flex gap-2">
            <UTooltip 
              :text="fraudCase.status === 'pending' ? 'Please start the analysis first' : ''"
              :disabled="fraudCase.status !== 'pending'"
            >
              <UButton
                label="Chat Assistant"
                icon="i-lucide-message-circle"
                color="secondary"
                variant="outline"
                :disabled="fraudCase.status === 'pending'"
                @click="openChatAssistant"
              />
            </UTooltip>
            <UButton
              v-if="fraudCase.status === 'pending'"
              label="Start Analysis"
              icon="i-lucide-zap"
              color="primary"
              :loading="loading"
              @click="analyzeCase"
            />
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6">
        <!-- Pending Alert - Full Width -->
        <div v-if="fraudCase.status === 'pending' && showPendingAlert" class="relative">
          <UAlert
            icon="i-lucide-alert-circle"
            color="warning"
            variant="soft"
            title="Analysis Pending"
            description="This case is ready for analysis. Click the 'Start Analysis' button in the top-right to begin AI-powered fraud detection and analysis."
          />
          <UButton
            icon="i-lucide-x"
            color="neutral"
            variant="ghost"
            size="sm"
            class="absolute top-2 right-2"
            @click="showPendingAlert = false"
          /> 
        </div>

        <!-- Analyzing Alert - Full Width -->
        <div v-if="fraudCase.status === 'analyzing' && showPendingAlert" class="relative">
          <UAlert
            icon="i-lucide-loader"
            color="info"
            variant="soft"
            title="Analysis in Progress"
            description="The AI is currently analyzing this case. Click the refresh button to check if the analysis is complete."
          />
          <div class="absolute top-2 right-2 flex gap-2">
            <UButton
              icon="i-lucide-refresh-cw"
              color="info"
              variant="outline"
              size="sm"
              :loading="loading"
              @click="fetchCase"
            />
            <UButton
              icon="i-lucide-x"
              color="neutral"
              variant="ghost"
              size="sm"
              @click="showPendingAlert = false"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Case Overview Card -->
          <UPageCard variant="soft" title="Case Overview">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted">Status</p>
                  <UBadge :color="statusColor as any" variant="soft" class="capitalize mt-1">
                    {{ fraudCase.status }}
                  </UBadge>
                </div>
                <div class="text-right">
                  <p class="text-sm text-muted">Created</p>
                  <p class="font-medium">{{ fraudCase.created_at ? new Date(fraudCase.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A' }}</p>
                </div>
              </div>

              <div class="border-t border-default pt-4">
                <p class="text-sm text-muted mb-2">Description</p>
                <p class="text-base leading-relaxed">{{ fraudCase.description }}</p>
              </div>
            </div>
          </UPageCard>

          <!-- Files Section -->
          <UPageCard variant="soft" title="Document Management">
            <div class="space-y-4">
              <!-- Files from case data -->
              <div v-if="fraudCase.files && fraudCase.files.length > 0" class="space-y-2">
                <p class="text-sm font-medium text-highlighted">Uploaded Files ({{ fraudCase.files.length }})</p>
                <div
                  v-for="(file, idx) in fraudCase.files"
                  :key="idx"
                  class="flex items-center gap-3 p-3 rounded-lg bg-elevated/50 hover:bg-elevated transition-colors group"
                >
                  <UIcon name="i-lucide-file" class="w-5 h-5 text-primary shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <a
                        :href="typeof file === 'string' ? file : file.url"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="text-sm font-medium text-primary hover:underline truncate"
                      >
                        {{ (typeof file === 'string' ? file : file.name || file.url).split('/').pop() }}
                      </a>
                      <UBadge 
                        v-if="typeof file === 'object' && file.classification"
                        :label="file.classification"
                        variant="subtle"
                        size="sm"
                        :color="getClassificationColor(file.classification)"
                        class="shrink-0"
                      />
                    </div>
                    <p v-if="typeof file === 'object' && file.description" class="text-xs text-muted">{{ file.description }}</p>
                  </div>
                  <UButton
                    icon="i-lucide-trash-2"
                    color="error"
                    variant="ghost"
                    size="xs"
                    :loading="loading"
                    @click="onDeleteFile((typeof file === 'string' ? file : file.url).split('/').pop() || '')"
                    class="opacity-0 group-hover:opacity-100 transition-opacity"
                  />
                </div>
              </div>

              <!-- Empty state -->
              <div v-else class="text-center py-8">
                <UIcon name="i-lucide-inbox" class="w-8 h-8 text-muted mx-auto mb-2" />
                <p class="text-sm text-muted">No files uploaded yet</p>
              </div>

              <!-- Upload new files section -->
              <div class="border-t border-default pt-4 mt-4">
                <CaseFileUploader :case-id="caseId" @file-uploaded="onFileUploaded" />
              </div>
            </div>
          </UPageCard>

          <!-- AI Insights Section -->
          <UPageCard v-if="fraudCase.insights && fraudCase.insights.length > 0" variant="soft" title="AI Insights">
            <div class="space-y-3">
              <div v-for="(insight, idx) in fraudCase.insights" :key="idx" class="flex gap-3">
                <UIcon name="i-lucide-lightbulb" class="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                <p class="text-sm leading-relaxed">{{ insight }}</p>
              </div>
            </div>
          </UPageCard>

          <!-- Applicable Laws Section -->
          <UPageCard v-if="fraudCase.applicable_laws && fraudCase.applicable_laws.length > 0" variant="soft" title="Applicable Indonesian Laws (UU)">
            <div class="space-y-4">
              <!-- Law Impact Analysis Summary -->
              <div v-if="fraudCase.law_impact_analysis" class="p-4 rounded-lg bg-red-50 border border-red-200">
                <div class="flex gap-3">
                  <UIcon name="i-lucide-alert-triangle" class="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                  <div class="flex-1">
                    <h4 class="text-sm font-semibold text-red-900 mb-2">Legal Impact Analysis</h4>
                    <p class="text-sm text-red-800 leading-relaxed">{{ fraudCase.law_impact_analysis }}</p>
                  </div>
                </div>
              </div>

              <!-- Laws List -->
              <div class="space-y-4">
                <div v-for="(law, idx) in fraudCase.applicable_laws" :key="idx" class="border border-default rounded-lg p-4 hover:bg-elevated/30 transition-colors">
                  <!-- Law Name -->
                  <div class="flex items-start gap-3 mb-3">
                    <UIcon name="i-lucide-book" class="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <div class="flex-1">
                      <h5 class="text-sm font-semibold text-highlighted">{{ law.law_name }}</h5>
                    </div>
                  </div>

                  <!-- Articles -->
                  <div class="mb-3 pl-8">
                    <p class="text-xs font-medium text-muted uppercase tracking-wide mb-2">Relevant Articles:</p>
                    <div class="flex flex-wrap gap-2">
                      <UBadge 
                        v-for="(article, aIdx) in law.articles" 
                        :key="aIdx"
                        :label="article"
                        variant="subtle"
                        color="primary"
                        size="sm"
                      />
                    </div>
                  </div>

                  <!-- Violation Description -->
                  <div class="mb-3 pl-8">
                    <p class="text-xs font-medium text-muted uppercase tracking-wide mb-1">Violation Description:</p>
                    <p class="text-sm leading-relaxed">{{ law.violation_description }}</p>
                  </div>

                  <!-- Penalty Level -->
                  <div class="pl-8 p-3 rounded-lg bg-error/5 border border-error/20">
                    <div class="flex items-start gap-2">
                      <UIcon name="i-lucide-alert-circle" class="w-4 h-4 text-error shrink-0 mt-0.5" />
                      <div>
                        <p class="text-xs font-medium text-error uppercase tracking-wide mb-1">Penalty</p>
                        <p class="text-sm text-error/90">{{ law.penalty_level }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </UPageCard>

          <!-- Analysis Section -->
          <UPageCard v-if="fraudCase.analysis" variant="soft" title="Detailed Analysis">
            <div class="space-y-6">
              <!-- Data Review -->
              <div v-if="fraudCase.analysis.data_review" class="space-y-2">
                <div class="flex items-center gap-2">
                  <UIcon name="i-lucide-database" class="w-5 h-5 text-blue-500" />
                  <h4 class="text-sm font-semibold">Data Review</h4>
                </div>
                <div class="pl-7 prose prose-sm dark:prose-invert max-w-none" v-html="parseMarkdown(fraudCase.analysis.data_review)"></div>
              </div>

              <!-- Root Cause Analysis -->
              <div v-if="fraudCase.analysis.root_cause_analysis" class="space-y-2 border-t border-default pt-4">
                <div class="flex items-center gap-2">
                  <UIcon name="i-lucide-search" class="w-5 h-5 text-orange-500" />
                  <h4 class="text-sm font-semibold">Root Cause Analysis</h4>
                </div>
                <div class="pl-7 prose prose-sm dark:prose-invert max-w-none" v-html="parseMarkdown(fraudCase.analysis.root_cause_analysis)"></div>
              </div>

              <!-- Hypothesis Testing -->
              <div v-if="fraudCase.analysis.hypothesis_testing" class="space-y-2 border-t border-default pt-4">
                <div class="flex items-center gap-2">
                  <UIcon name="i-lucide-microscope" class="w-5 h-5 text-purple-500" />
                  <h4 class="text-sm font-semibold">Hypothesis Testing</h4>
                </div>
                <div class="pl-7 prose prose-sm dark:prose-invert max-w-none" v-html="parseMarkdown(fraudCase.analysis.hypothesis_testing)"></div>
              </div>
            </div>
          </UPageCard>

          <!-- Recommendations Section -->
          <UPageCard v-if="fraudCase.recommendations && fraudCase.recommendations.length > 0" variant="soft" title="Recommendations">
            <div class="space-y-3">
              <div v-for="(rec, idx) in fraudCase.recommendations" :key="idx" class="flex gap-3">
                <div class="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary shrink-0 text-sm font-medium">
                  {{ idx + 1 }}
                </div>
                <p class="text-sm leading-relaxed pt-0.5">{{ rec }}</p>
              </div>
            </div>
          </UPageCard>

          <!-- v-network-graph Visualization -->
          <UPageCard variant="soft" title="Investigative Mind Map">
            <div class="w-full bg-white rounded-lg border border-gray-200" style="height: 500px;">
              <v-network-graph
                class="w-full h-full"
                :nodes="nodes"
                :edges="edges"
                :configs="configs"
                :layouts="vNetworkGraphLayouts"
              >
                <template #edge-label="{ edge, ...slotProps }">
                  <v-edge-label 
                  :text="edge.label" 
                  vertical-align="center" 
                  v-bind="slotProps" />
                </template>
              </v-network-graph>
            </div>
                <div class="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full bg-blue-500"></div>
                  <span class="text-sm text-white font-medium">{{ Object.keys(nodes).length }} Entities</span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="w-8 h-0.5 bg-gray-300"></div>
                  <span class="text-sm text-white font-medium">{{ Object.keys(edges).length }} Relations</span>
                </div>
                <div class="flex items-center gap-2">
                  <UIcon name="i-lucide-move" class="w-4 h-4 text-gray-600" />
                  <span class="text-sm text-white">Drag to move</span>
                </div>
              </div>
          </UPageCard>
          
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Analysis Journey -->
          <UPageCard variant="soft" title="Analysis Journey">
            <div class="space-y-3">
              <!-- Step 1: Case Created -->
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-3 h-3 rounded-full bg-success"></div>
                  <div class="w-0.5 h-8 bg-success/30 my-1"></div>
                </div>
                <div class="flex-1 pt-0.5">
                  <p class="text-sm font-medium">Case Created</p>
                  <p class="text-xs text-muted">{{ fraudCase.created_at ? new Date(fraudCase.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A' }}</p>
                </div>
              </div>

              <!-- Step 2: Analyzing -->
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div :class="[
                    'w-3 h-3 rounded-full',
                    fraudCase.status === 'pending' ? 'bg-muted' : fraudCase.status === 'analyzing' ? 'bg-info animate-pulse' : 'bg-success'
                  ]"></div>
                  <div :class="[
                    'w-0.5 h-8 my-1',
                    fraudCase.status === 'pending' ? 'bg-muted/30' : fraudCase.status === 'analyzing' ? 'bg-info/30' : 'bg-success/30'
                  ]"></div>
                </div>
                <div class="flex-1 pt-0.5">
                  <p class="text-sm font-medium">Analyzing</p>
                  <p class="text-xs text-muted">{{ fraudCase.status === 'analyzing' ? 'In progress...' : 'Ready for analysis' }}</p>
                </div>
              </div>

              <!-- Step 3: Analysis Completed -->
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div :class="[
                    'w-3 h-3 rounded-full',
                    ['completed', 'archived'].includes(fraudCase.status) ? 'bg-success' : 'bg-muted/50'
                  ]"></div>
                </div>
                <div class="flex-1 pt-0.5">
                  <p class="text-sm font-medium">Analysis Completed</p>
                  <p class="text-xs text-muted">{{ ['completed', 'archived'].includes(fraudCase.status) ? 'Insights and recommendations available' : 'Pending' }}</p>
                </div>
              </div>
            </div>
          </UPageCard>

          <!-- Case Stats -->
          <UPageCard variant="soft" title="Case Statistics">
            <div class="space-y-3">
              <div class="flex justify-between items-center p-2 rounded bg-elevated/50">
                <span class="text-sm text-muted">Files</span>
                <span class="font-medium">{{ fraudCase.files.length }}</span>
              </div>
              <div class="flex justify-between items-center p-2 rounded bg-elevated/50">
                <span class="text-sm text-muted">Insights Found</span>
                <span class="font-medium">{{ fraudCase.insights ? 'Yes' : 'No' }}</span>
              </div>
              <div class="flex justify-between items-center p-2 rounded bg-elevated/50">
                <span class="text-sm text-muted">Recommendations</span>
                <span class="font-medium">{{ fraudCase.recommendations?.length || 0 }}</span>
              </div>
              <div v-if="fraudCase.case_main_category" class="border-t border-default pt-3 mt-3">
                <div class="flex justify-between items-center p-2 rounded bg-elevated/50 mb-2">
                  <span class="text-sm text-muted">Main Category</span>
                  <span class="font-medium text-xs">{{ fraudCase.case_main_category }}</span>
                </div>
                <div v-if="fraudCase.case_sub_category" class="flex justify-between items-center p-2 rounded bg-elevated/50">
                  <span class="text-sm text-muted">Sub Category</span>
                  <span class="font-medium text-xs">{{ fraudCase.case_sub_category }}</span>
                </div>
              </div>
            </div>
          </UPageCard>

          <!-- Notes Section -->
          <UPageCard variant="soft" title="Notes">
            <div class="space-y-4">
              <!-- Input Box -->
              <div class="space-y-2">
                <UTextarea
                  v-model="newNote"
                  placeholder="Add a quick note..."
                  :rows="3"
                  class="w-full"
                />
                <UButton
                  label="Add Note"
                  icon="i-lucide-plus"
                  color="primary"
                  size="sm"
                  :loading="notesLoading"
                  :disabled="!newNote.trim()"
                  @click="addNote"
                  class=""
                />
              </div>

              <!-- Notes List -->
              <div v-if="fraudCase.notes && fraudCase.notes.length > 0" class="space-y-2 border-t border-default pt-4">
                <div
                  v-for="(note, idx) in fraudCase.notes"
                  :key="note.id || idx"
                  class="p-3 rounded-lg bg-elevated/50 hover:bg-elevated transition-colors group"
                >
                  <div class="flex items-start justify-between gap-2 mb-1">
                    <p class="text-xs text-muted">{{ note.created_at ? new Date(note.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'Just now' }}</p>
                    <UButton
                      icon="i-lucide-trash-2"
                      color="error"
                      variant="ghost"
                      size="xs"
                      :loading="notesLoading"
                      @click="deleteNote(note.id || '')"
                      class="opacity-0 group-hover:opacity-100 transition-opacity"
                    />
                  </div>
                  <p class="text-sm leading-relaxed">{{ note.content }}</p>
                </div>
              </div>

              <!-- Empty state -->
              <div v-else class="text-center py-4">
                <p class="text-xs text-muted">No notes yet. Add one to get started!</p>
              </div>
            </div>
          </UPageCard>
        </div>
        </div>
      </div>
    </template>
  </UDashboardPanel>

  <!-- Loading State -->
  <UDashboardPanel v-else id="case-detail-loading">
    <template #header>
      <UDashboardNavbar title="Loading...">
        <template #leading>
          <UButton
            icon="i-lucide-arrow-left"
            color="neutral"
            variant="ghost"
            @click="router.push('/cases')"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3"></div>
          <p class="text-muted">Loading case details...</p>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
