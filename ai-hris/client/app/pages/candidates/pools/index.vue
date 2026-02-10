<script setup lang="ts">
import { Search, MessageCircle, Eye, Send, X, Filter } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface Candidate {
  id: string
  candidateId: string
  name: string
  role: string
  matchScore?: number
  skills: string[]
  experience: string
  location: string
  avatar: string
}

const dummyCandidates: Candidate[] = [
  {
    id: "1",
    candidateId: "c1",
    name: "Sarah Wijaya",
    role: "UX Designer",
    skills: ["UX Designing", "Figma", "Design Systems"],
    experience: "5 years",
    location: "Jakarta",
    avatar: "https://images.generated.photos/HY_ndz04cKVnrFLxjCqEjSKFas_Gw9A6gua5c5WVsEg/rs:fit:512:512/wm:0.95:sowe:18:18:0.33/czM6Ly9pY29uczgu/Z3Bob3Rvcy1wcm9k/LnBob3Rvcy92M18w/MjQwOTYyLmpwZw.jpg",
    matchScore: undefined
  },
  {
    id: "2",
    candidateId: "c2",
    name: "Budi Santoso",
    role: "UI Designer",
    skills: ["UI Design", "Prototyping", "Research"],
    experience: "3 years",
    location: "Bandung",
    avatar: "https://images.generated.photos/9vsrj4-ESDtoejXpW1T_0uvAOwO9gyEjD_jAyc9UKPo/rs:fit:512:512/wm:0.95:sowe:18:18:0.33/czM6Ly9pY29uczgu/Z3Bob3Rvcy1wcm9k/LnBob3Rvcy92M18w/OTE4NTM1LmpwZw.jpg",
    matchScore: undefined
  },
  {
    id: "3",
    candidateId: "c3",
    name: "Citra Lestari",
    role: "Product Strategy",
    skills: ["Product Strategy", "Wireframing", "User Research"],
    experience: "9 years",
    location: "Surabaya",
    avatar: "https://images.generated.photos/4LF_5AVt-cVTZJPfd_BSg6ol0QMuXA94zqn9Ua6oh0c/rs:fit:512:512/wm:0.95:sowe:18:18:0.33/czM6Ly9pY29uczgu/Z3Bob3Rvcy1wcm9k/LnBob3Rvcy92M18w/ODkzODI3LmpwZw.jpg",
    matchScore: undefined
  },
  {
    id: "4",
    candidateId: "c4",
    name: "Eko Prasetyo",
    role: "Frontend Developer",
    skills: ["Vue.js", "React", "TypeScript", "Tailwind"],
    experience: "4 years",
    location: "Jakarta",
    avatar: "https://images.generated.photos/belPAh1isDveQYW514isbu2T63Yrt1bNBRIruaxJd_w/rs:fit:512:512/wm:0.95:sowe:18:18:0.33/czM6Ly9pY29uczgu/Z3Bob3Rvcy1wcm9k/LnBob3Rvcy92M18w/MzYzNDIxLmpwZw.jpg",
    matchScore: undefined
  },
  {
    id: "5",
    candidateId: "c5",
    name: "Dian Sastro",
    role: "Data Scientist",
    skills: ["Python", "Machine Learning", "SQL", "Pandas"],
    experience: "6 years",
    location: "Remote",
    avatar: "https://images.generated.photos/24qkv6kYfVeFy3WZkSprhkEdAFUCon6DhRFndm2lBUk/rs:fit:512:512/wm:0.95:sowe:18:18:0.33/czM6Ly9pY29uczgu/Z3Bob3Rvcy1wcm9k/LnBob3Rvcy92M18w/NzAzNTU3LmpwZw.jpg",
    matchScore: undefined
  }
]

const allCandidates = ref<Candidate[]>([...dummyCandidates])
const candidates = ref<Candidate[]>([...dummyCandidates])
const isSearchActive = ref(false)
const isLoading = ref(false)

const jobTitles = ["UX Designer", "UI Designer", "Product Manager", "Frontend Developer", "Backend Developer", "Data Scientist"]
const locations = ["Jakarta", "Bandung", "Surabaya", "Remote", "Yogyakarta", "Bali"]
const experienceLevels = ["Junior", "Mid-Level", "Senior", "Lead"]

const selectedJob = ref("")
const selectedLocation = ref("")
const selectedExperience = ref("")
const searchQuery = ref("")

const handleSearch = async () => {
  isLoading.value = true
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 600))

  try {
    let results = [...allCandidates.value]

    // 1. Search Logic (Simulated AI Matching)
    // Enable match score if there is a search query OR any filter is active
    const hasFilter = selectedJob.value || selectedLocation.value || selectedExperience.value
    
    if (searchQuery.value || hasFilter) {
      isSearchActive.value = true
      const query = searchQuery.value.toLowerCase()
      
      results = results.map(c => {
        // Simple scoring simulation
        let score = 0
        const text = `${c.name} ${c.role} ${c.skills.join(' ')}`.toLowerCase()
        
        if (searchQuery.value) {
            // If searching, score based on text relevance
            if (text.includes(query)) {
                score = 80 + Math.floor(Math.random() * 15) // High score if match
            } else {
                score = 40 + Math.floor(Math.random() * 40) // Random low score
            }
        } else {
            // If only filtering, give high scores to imply they match the criteria
            score = 85 + Math.floor(Math.random() * 10)
        }
        
        return { ...c, matchScore: score }
      })
      
      // Sort by score
      results.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
    } else {
      isSearchActive.value = false
      results = results.map(c => ({ ...c, matchScore: undefined }))
    }

    // 2. Apply Filters
    if (selectedJob.value) {
      results = results.filter(c => c.role.toLowerCase().includes(selectedJob.value.toLowerCase()))
    }
    if (selectedLocation.value) {
      results = results.filter(c => c.location.toLowerCase().includes(selectedLocation.value.toLowerCase()))
    }
    if (selectedExperience.value) {
       results = results.filter(c => {
         const exp = parseInt(c.experience) || 0
         if (selectedExperience.value === "Junior") return exp <= 2
         if (selectedExperience.value === "Mid-Level") return exp > 2 && exp <= 5
         if (selectedExperience.value === "Senior") return exp > 5
         return true
       })
    }

    candidates.value = results
  } finally {
    isLoading.value = false
  }
}

const handleReset = () => {
  selectedJob.value = ""
  selectedLocation.value = ""
  selectedExperience.value = ""
  searchQuery.value = ""
  isSearchActive.value = false
  candidates.value = [...allCandidates.value].map(c => ({ ...c, matchScore: undefined }))
}

const handleChat = () => {
  console.log("Open chat")
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-3xl font-bold tracking-tight">Candidate Pools</h2>
        <p class="text-muted-foreground mt-1">
          AI-powered matching based on skills, experience, and historical data.
        </p>
      </div>
    </div>

    <!-- Filters Toolbar -->
    <div class="flex flex-col gap-4 p-4 border rounded-lg bg-card">
      <div class="flex flex-col md:flex-row gap-4 items-end md:items-center">
        <!-- Search Input -->
        <div class="w-full md:w-1/3 relative">
           <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
           <Input v-model="searchQuery" placeholder="Search by name, skills, or keywords..." class="pl-9" />
        </div>
        
        <!-- Filters Group -->
        <div class="flex flex-1 gap-2 overflow-x-auto pb-2 md:pb-0 w-full md:w-auto">
             <Select v-model="selectedJob">
                <SelectTrigger class="w-full md:w-[180px]">
                  <SelectValue placeholder="Job Title" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="job in jobTitles" :key="job" :value="job">
                    {{ job }}
                  </SelectItem>
                </SelectContent>
              </Select>

             <Select v-model="selectedLocation">
                <SelectTrigger class="w-full md:w-[180px]">
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="loc in locations" :key="loc" :value="loc">
                    {{ loc }}
                  </SelectItem>
                </SelectContent>
              </Select>

             <Select v-model="selectedExperience">
                <SelectTrigger class="w-full md:w-[180px]">
                  <SelectValue placeholder="Experience" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="exp in experienceLevels" :key="exp" :value="exp">
                    {{ exp }}
                  </SelectItem>
                </SelectContent>
              </Select>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2 w-full md:w-auto">
             <Button variant="outline" size="icon" @click="handleReset" title="Reset Filters">
                <X class="h-4 w-4" />
             </Button>
             <Button @click="handleSearch" class="flex-1 md:flex-none">
              Search
            </Button>
        </div>
      </div>
    </div>


    <!-- Results Table -->
    <div class="rounded-md border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Candidate</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Experience</TableHead>
            <TableHead>Location</TableHead>
            <TableHead v-if="isSearchActive" class="w-[250px]">Match Score</TableHead>
            <TableHead>Skills</TableHead>
            <TableHead class="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-if="isLoading">
             <TableCell colspan="7" class="h-24 text-center">
                <div class="flex items-center justify-center gap-2">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  Searching...
                </div>
             </TableCell>
          </TableRow>
          <TableRow v-else-if="candidates.length === 0">
             <TableCell colspan="7" class="h-24 text-center text-muted-foreground">
                No candidates found.
             </TableCell>
          </TableRow>
          <TableRow v-else v-for="candidate in candidates" :key="candidate.id">
            <TableCell>
              <div class="flex items-center gap-3">
                <Avatar class="h-9 w-9">
                  <AvatarImage :src="candidate.avatar" :alt="candidate.name" />
                  <AvatarFallback>{{ candidate.name.charAt(0) }}</AvatarFallback>
                </Avatar>
                <div class="font-medium">{{ candidate.name }}</div>
              </div>
            </TableCell>
            <TableCell>
              <Badge variant="secondary" class="font-normal">{{ candidate.role }}</Badge>
            </TableCell>
            <TableCell>{{ candidate.experience }}</TableCell>
            <TableCell>{{ candidate.location }}</TableCell>
            <TableCell v-if="isSearchActive">
              <div class="flex items-center gap-3">
                <Progress :model-value="candidate.matchScore" class="h-2 w-24" />
                <span class="text-sm font-bold" :class="(candidate.matchScore || 0) > 85 ? 'text-green-600' : 'text-blue-600'">{{ candidate.matchScore }}%</span>
              </div>
            </TableCell>
            <TableCell>
              <div class="flex flex-wrap gap-1 max-w-[200px]">
                <Badge v-for="skill in candidate.skills.slice(0, 2)" :key="skill" variant="outline" class="text-xs font-normal">
                    {{ skill }}
                </Badge>
                <Badge v-if="candidate.skills.length > 2" variant="outline" class="text-xs font-normal">+{{ candidate.skills.length - 2 }}</Badge>
              </div>
            </TableCell>
            <TableCell class="text-right">
              <div class="flex justify-end gap-2">
                <Button variant="ghost" size="icon" title="View Profile">
                  <Eye class="h-4 w-4 text-muted-foreground" />
                </Button>
                <Button variant="ghost" size="icon" title="Invite">
                  <Send class="h-4 w-4 text-blue-600" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Chat FAB -->
    <div class="fixed bottom-8 right-8">
      <Button 
        size="icon" 
        class="h-12 w-12 rounded-full shadow-lg"
        @click="handleChat"
      >
        <MessageCircle class="h-6 w-6" />
      </Button>
    </div>
  </div>
</template>