<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Candidate } from '@/components/candidates/data/schema'
import candidatesData from '@/components/candidates/data/candidates.json'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Send,
  MoveRight,
  Download,
  AlertTriangle,
  MapPin,
  Clock,
  Calendar,
  Headphones,
  Gem,
  FileText,
  Info,
  MessageSquare,
  Activity,
  ExternalLink,
  Briefcase,
  CreditCard,
  Users,
  GraduationCap,
  IdCard,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const candidates = (candidatesData as { data: Candidate[] }).data
const candidateId = route.params.id as string
const candidate = computed(() => candidates.find(c => c.id === candidateId))

const activeTab = ref('info')

// Mock extended data for the UI
const extendedCandidate = computed(() => {
  if (!candidate.value) return null
  
  return {
    ...candidate.value,
    role: 'Product Designer I', // Mock role
    location: 'Amsterdam, The Netherlands',
    daysInGoodfit: 3,
    birthday: 'October 14, 1994 (31 years old)',
    signals: [
      { label: 'Short Tenure', color: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: 'briefcase' },
      { label: 'Proctoring Incident', color: 'bg-red-100 text-red-800 border-red-200', icon: 'alert' },
      { label: 'Quick Joiner', color: 'bg-green-100 text-green-800 border-green-200', icon: 'zap' },
    ],
    scores: {
      aiInterview: 8.0,
      assessments: 4.9,
      resume: 7.3
    },
    interviewScores: [
      { label: 'Visual Design', value: 8.5, color: 'bg-green-500' },
      { label: 'Communication', value: 7.2, color: 'bg-blue-500' },
      { label: 'Problem Solving', value: 6.8, color: 'bg-purple-500' }
    ],
    experience: [
      { role: 'Human Interface Designer', company: 'Apple, Inc.', period: '2024 - present' },
      { role: 'Product Designer', company: 'Uber', period: '2019-2024' }
    ],
    education: [
      { school: 'National Institute of Design', period: '2015-2019' },
      { school: 'National Institute of Fashion Technology', period: '2012-2015' }
    ],
    documents: [
      { type: 'KTP', name: 'ktp_scan.jpg', icon: IdCard },
      { type: 'Kartu Keluarga', name: 'kk_scan.pdf', icon: Users },
      { type: 'Ijazah', name: 'ijazah_s1.pdf', icon: GraduationCap },
      { type: 'Buku Tabungan', name: 'buku_tabungan_bca.jpg', icon: CreditCard }
    ],
    notes: [
      { author: 'Sarah Miller', role: 'Hiring Manager', date: '2 days ago', content: 'Strong portfolio, but I have concerns about the short tenure at the previous role. Let\'s dig deeper into that during the interview.' },
      { author: 'James Chen', role: 'Recruiter', date: '3 days ago', content: 'Candidate was very responsive and enthusiastic during the initial screening.' }
    ],
    activities: [
      { title: 'Moved to Interview Stage', date: '2 days ago', description: 'Candidate was moved from Screening to Interview stage.' },
      { title: 'AI Interview Completed', date: '3 days ago', description: 'Candidate completed the AI interview with a score of 8.0/10.' },
      { title: 'Application Received', date: '4 days ago', description: 'Candidate applied for Product Designer I position.' }
    ]
  }
})

const downloadCV = () => {
  if (candidate.value?.cv_url) {
    window.open(candidate.value.cv_url, '_blank')
  }
}
</script>

<template>
  <div v-if="extendedCandidate" class="min-h-screen bg-muted/40">
    <div class="max-w-7xl mx-auto p-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left Column (Main Content) -->
        <div class="lg:col-span-8 space-y-6">
          
          <!-- Profile Header -->
          <div class="flex flex-col sm:flex-row gap-6 items-start">
            <div class="relative">
              <Avatar class="h-24 w-24 border-4 border-background shadow-sm">
                <AvatarImage :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${extendedCandidate.name}`" />
                <AvatarFallback>{{ extendedCandidate.name.charAt(0) }}</AvatarFallback>
              </Avatar>
              <Badge class="absolute -bottom-2 -right-2 bg-green-100 text-green-700 hover:bg-green-100 border-green-200 px-2 py-0.5 text-sm font-bold shadow-sm">
                {{ extendedCandidate.scores.aiInterview }}/10
              </Badge>
            </div>
            
            <div class="flex-1 space-y-2">
              <div class="flex justify-between items-start">
                <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                  <h1 class="text-3xl font-bold tracking-tight text-foreground">{{ extendedCandidate.name }}</h1>
                  <span class="text-lg text-muted-foreground">for {{ extendedCandidate.role }}</span>
                </div>
              </div>
              
              <div class="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <div class="flex items-center gap-1.5">
                  <MapPin class="h-4 w-4" />
                  {{ extendedCandidate.location }}
                </div>
                <div class="flex items-center gap-1.5">
                  <Clock class="h-4 w-4" />
                  {{ extendedCandidate.daysInGoodfit }} days in Goodfit
                </div>
                <div class="flex items-center gap-1.5">
                  <Calendar class="h-4 w-4" />
                  Applied {{ Math.floor((new Date().getTime() - new Date(extendedCandidate.appliedDate).getTime()) / (1000 * 3600 * 24)) }} days ago
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-wrap gap-3">
            <Button class="bg-blue-600 hover:bg-blue-700 text-white gap-2">
              <Send class="h-4 w-4" />
              Send Mail
            </Button>
            <Button variant="outline" class="gap-2">
              <MoveRight class="h-4 w-4" />
              Move to stage
            </Button>
            <Button variant="outline" class="gap-2" @click="downloadCV">
              <Download class="h-4 w-4" />
              Download Candidate Report
            </Button>
            <Button variant="outline" size="icon" class="text-amber-500 border-amber-200 hover:bg-amber-50">
              <AlertTriangle class="h-4 w-4" />
            </Button>
          </div>

          <!-- Info Banner -->
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-lg p-3 flex items-center justify-between text-blue-700 dark:text-blue-300 text-sm">
            <span class="font-medium">{{ extendedCandidate.name }} is interviewing for 2 more roles</span>
            <ChevronRight class="h-4 w-4 opacity-60" />
          </div>

          <!-- Signals -->
          <div class="space-y-3">
            <h3 class="text-sm font-medium text-muted-foreground">Signals</h3>
            <div class="flex flex-wrap gap-3">
              <Badge 
                v-for="signal in extendedCandidate.signals" 
                :key="signal.label" 
                variant="outline"
                :class="['gap-1.5 py-1.5 px-3 text-sm font-normal', signal.color]"
              >
                <Briefcase v-if="signal.icon === 'briefcase'" class="h-3.5 w-3.5" />
                <AlertTriangle v-else-if="signal.icon === 'alert'" class="h-3.5 w-3.5" />
                <Activity v-else class="h-3.5 w-3.5" />
                {{ signal.label }}
              </Badge>
            </div>
          </div>

          <!-- AI Interview Summary -->
          <div class="space-y-3">
            <h3 class="text-sm font-medium text-muted-foreground">AI Interview Summary</h3>
            <p class="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
              {{ (extendedCandidate.notes || '') + '\n\nLorem ipsum dolor sit amet consectetur. Nulla risus nisl magna platea in convallis. Vitae elementum pellentesque elit augue massa. Lectus sit nisl vitae a. Massa felis aliquot amet habitasse. Scelerisque ut proin nescitur non ornare. Ut amet mauris nulla cursus cum mauris ac tempor. In sed condimentum nullam sed in. Nibh dui mattis ornare bibendum nullam risus ut pharetra. Sed ultrices tempus amet egestas hac arcu. Ut a convallis pellentesque sem ipsum bibendum. Arcu nulla dictum sit enim at vulputate. Congue odio risus amet egestas nec diam consequat venenatis. This will contain both info and a summary of recommended actionable for the candidate.\n\nPraesent sapien massa, convallis a pellentesque nec, egestas non nisi. Curabitur arcu erat, accumsan id imperdiet et, porttitor at sem. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Nulla quis lorem ut libero malesuada feugiat. Vivamus magna justo, lacinia eget consectetur sed, convallis at tellus. Quisque velit nisi, pretium ut lacinia in, elementum id enim.\n\nDonec sollicitudin molestie malesuada. Cras ultricies ligula sed magna dictum porta. Curabitur aliquet quam id dui posuere blandit. Curabitur non nulla sit amet nisl tempus convallis quis ac lectus. Proin eget tortor risus. Mauris blandit aliquet elit, eget tincidunt nibh pulvinar a.' }}
            </p>
          </div>

          <!-- Score Cards -->
          <div class="space-y-3">
            <h3 class="text-sm font-medium text-muted-foreground">Score</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card class="bg-green-50/50 dark:bg-green-900/10 border-green-100 dark:border-green-900/20">
                <CardContent class="p-4 flex items-center gap-4">
                  <div class="h-10 w-10 rounded-full bg-background flex items-center justify-center shadow-sm text-green-600 dark:text-green-400">
                    <Headphones class="h-5 w-5" />
                  </div>
                  <div>
                    <div class="text-2xl font-bold text-foreground">{{ extendedCandidate.scores.aiInterview.toFixed(1) }}</div>
                    <div class="text-xs font-medium text-muted-foreground">AI Interview</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card class="bg-red-50/50 dark:bg-red-900/10 border-red-100 dark:border-red-900/20">
                <CardContent class="p-4 flex items-center gap-4">
                  <div class="h-10 w-10 rounded-full bg-background flex items-center justify-center shadow-sm text-red-600 dark:text-red-400">
                    <Gem class="h-5 w-5" />
                  </div>
                  <div>
                    <div class="text-2xl font-bold text-foreground">{{ extendedCandidate.scores.assessments.toFixed(1) }}</div>
                    <div class="text-xs font-medium text-muted-foreground">Assessments</div>
                  </div>
                </CardContent>
              </Card>
              
              <Card class="bg-muted/50 border-border">
                <CardContent class="p-4 flex items-center gap-4">
                  <div class="h-10 w-10 rounded-full bg-background flex items-center justify-center shadow-sm text-muted-foreground">
                    <FileText class="h-5 w-5" />
                  </div>
                  <div>
                    <div class="text-2xl font-bold text-foreground">{{ extendedCandidate.scores.resume.toFixed(1) }}</div>
                    <div class="text-xs font-medium text-muted-foreground">Resume</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <!-- AI Interview Score Details -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-base font-medium">AI Interview Score</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <div v-for="score in extendedCandidate.interviewScores" :key="score.label">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-muted-foreground">{{ score.label }}</span>
                  <span class="text-sm font-bold text-foreground">{{ score.value }}</span>
                </div>
                <div class="w-full bg-muted rounded-full h-2">
                  <div
                    class="h-2 rounded-full transition-all duration-500"
                    :class="score.color"
                    :style="{ width: `${(score.value / 10) * 100}%` }"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Right Column (Sidebar) -->
        <div class="lg:col-span-4 space-y-6">
          
          <!-- Tabs -->
          <div class="bg-muted/20 rounded-lg border p-1 flex gap-1">
            <Button 
              variant="ghost" 
              size="sm" 
              class="flex-1 transition-all"
              :class="activeTab === 'info' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
              @click="activeTab = 'info'"
            >
              <Info class="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              class="flex-1 transition-all"
              :class="activeTab === 'notes' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
              @click="activeTab = 'notes'"
            >
              <MessageSquare class="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              class="flex-1 transition-all"
              :class="activeTab === 'activity' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
              @click="activeTab = 'activity'"
            >
              <Activity class="h-4 w-4" />
            </Button>
          </div>

          <!-- Info Tab Content -->
          <div v-if="activeTab === 'info'" class="space-y-6">
            <!-- Contact Info -->
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Contact Info</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                  <span class="text-muted-foreground">Name</span>
                  <span class="font-medium text-right">{{ extendedCandidate.name }}</span>
                </div>
                <Separator />
                <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                  <span class="text-muted-foreground">Location</span>
                  <span class="font-medium text-right">{{ extendedCandidate.location }}</span>
                </div>
                <Separator />
                <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                  <span class="text-muted-foreground">Birthday</span>
                  <span class="font-medium text-right">{{ extendedCandidate.birthday }}</span>
                </div>
                <Separator />
                <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                  <span class="text-muted-foreground">Email</span>
                  <span class="font-medium text-right truncate text-blue-600">{{ extendedCandidate.email }}</span>
                </div>
              </CardContent>
            </Card>

            <!-- Experience -->
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Experience</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div v-for="(exp, i) in extendedCandidate.experience" :key="i" class="space-y-1">
                  <div class="font-medium text-sm">{{ exp.role }}, {{ exp.company }}</div>
                  <div class="text-xs text-muted-foreground">{{ exp.period }}</div>
                </div>
              </CardContent>
            </Card>

            <!-- Education -->
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Education</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div v-for="(edu, i) in extendedCandidate.education" :key="i" class="space-y-1">
                  <div class="font-medium text-sm">{{ edu.school }}</div>
                  <div class="text-xs text-muted-foreground">{{ edu.period }}</div>
                </div>
              </CardContent>
            </Card>

            <!-- Resume -->
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Résumé</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="border rounded-lg p-3 flex items-center justify-between bg-muted/50">
                  <div class="flex items-center gap-3 overflow-hidden">
                    <div class="h-8 w-8 bg-background rounded border flex items-center justify-center shrink-0">
                      <FileText class="h-4 w-4 text-red-500" />
                    </div>
                    <div class="flex flex-col overflow-hidden">
                      <span class="text-sm font-medium truncate">resume_{{ extendedCandidate.name.toLowerCase().split(' ')[0] }}.pdf</span>
                      <span class="text-xs text-muted-foreground">PDF Document</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" class="h-8 w-8" @click="downloadCV">
                    <ExternalLink class="h-4 w-4 text-muted-foreground" />
                  </Button>
                </div>
                
                <!-- Resume Preview Image (Mock) -->
                <div class="mt-3 border rounded-lg overflow-hidden bg-background h-32 flex items-center justify-center relative group cursor-pointer" @click="downloadCV">
                  <div class="absolute inset-0 bg-muted/30 flex flex-col items-center justify-center p-4">
                    <div class="w-full h-full bg-background shadow-sm p-2 text-[6px] text-muted-foreground overflow-hidden">
                        <div class="font-bold text-foreground text-[8px] mb-1">{{ extendedCandidate.name }}</div>
                        <div class="mb-1">PRODUCT DESIGNER</div>
                        <div class="space-y-1">
                          <div class="h-1 bg-muted w-full"></div>
                          <div class="h-1 bg-muted w-3/4"></div>
                          <div class="h-1 bg-muted w-5/6"></div>
                          <div class="h-1 bg-muted w-full"></div>
                          <div class="h-1 bg-muted w-1/2"></div>
                        </div>
                    </div>
                  </div>
                  <div class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors flex items-center justify-center">
                    <ExternalLink class="h-6 w-6 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <!-- Legal Documents -->
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Legal Documents</CardTitle>
              </CardHeader>
              <CardContent class="space-y-3">
                <div v-for="doc in extendedCandidate.documents" :key="doc.type" class="border rounded-lg p-3 flex items-center justify-between bg-muted/50">
                  <div class="flex items-center gap-3 overflow-hidden">
                    <div class="h-8 w-8 bg-background rounded border flex items-center justify-center shrink-0">
                      <component :is="doc.icon" class="h-4 w-4 text-blue-500" />
                    </div>
                    <div class="flex flex-col overflow-hidden">
                      <span class="text-sm font-medium truncate">{{ doc.name }}</span>
                      <span class="text-xs text-muted-foreground">{{ doc.type }}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" class="h-8 w-8">
                    <ExternalLink class="h-4 w-4 text-muted-foreground" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- Notes Tab Content -->
          <div v-else-if="activeTab === 'notes'" class="space-y-4">
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Internal Notes</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div v-for="(note, i) in extendedCandidate.notes" :key="i" class="flex gap-3">
                  <Avatar class="h-8 w-8 border">
                    <AvatarFallback class="text-xs">{{ note.author.charAt(0) }}</AvatarFallback>
                  </Avatar>
                  <div class="flex-1 space-y-1">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">{{ note.author }}</span>
                      <span class="text-xs text-muted-foreground">{{ note.date }}</span>
                    </div>
                    <p class="text-xs text-muted-foreground">{{ note.role }}</p>
                    <p class="text-sm text-foreground bg-muted/50 p-2 rounded-md mt-1">{{ note.content }}</p>
                  </div>
                </div>
                
                <div class="pt-2">
                  <Button variant="outline" class="w-full text-xs h-8">Add Note</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- Activity Tab Content -->
          <div v-else-if="activeTab === 'activity'" class="space-y-4">
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Activity Log</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="ml-2 border-l border-border space-y-8 my-2">
                  <div v-for="(activity, i) in extendedCandidate.activities" :key="i" class="relative pl-6">
                    <span class="absolute -left-[6.5px] top-1.5 h-3 w-3 rounded-full bg-primary ring-4 ring-background"></span>
                    <div class="flex flex-col gap-1">
                      <div class="flex items-center justify-between">
                        <span class="text-sm font-medium text-foreground">{{ activity.title }}</span>
                        <span class="text-xs text-muted-foreground">{{ activity.date }}</span>
                      </div>
                      <p class="text-sm text-muted-foreground">{{ activity.description }}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>
