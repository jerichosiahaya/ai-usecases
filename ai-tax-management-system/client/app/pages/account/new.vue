<script setup lang="ts">
import { ref } from 'vue'
import { toast } from 'vue-sonner'

const isUploading = ref(false)
const isExtracting = ref(false)
const extractedData = ref<any>(null)
const selectedAction = ref('pool') // 'pool' or 'job'
const selectedJob = ref('')

definePageMeta({
  layout: 'blank'
})

const dummyData = {
    "name": "Siti Nurhaliza",
    "email": "siti.nurhaliza@hotmail.com",
    "phone": "+62-812-0101",
    "gender": "Female",
    "dateOfBirth": "1992-05-15",
    "position": "Product Designer",
    "status": "hired",
    "appliedDate": "2025-11-20T07:13:36.180340Z",
    "address": {
        "detail": "Jln. Pemuda No 105 Rawamangun",
        "city": "Jakarta Timur",
        "country": "Indonesia",
        "zip": 335666
    },
    "salary": {
        "expectation": 18000000,
        "marketRange": {
            "min": 15000000,
            "max": 22000000,
            "currency": "IDR"
        },
        "status": "Within Budget",
        "confidence": 88,
        "analysis": "The candidate's expectation aligns well with the market rate for a Senior Product Designer in Jakarta. Given their experience at unicorn companies and strong portfolio, the request is competitive. Their background suggests they would bring significant value, justifying a placement in the mid-to-upper range of the market bracket.",
        "factors": [
            {
                "name": "Experience Match",
                "value": "High"
            },
            {
                "name": "Skill Premium",
                "value": "Moderate"
            },
            {
                "name": "Market Demand",
                "value": "Very High"
            }
        ]
    },
    "skills": [
        "Visual Design",
        "UX Research",
        "Figma",
        "Prototyping",
        "Design Systems"
    ],
    "rating": 4.8,
    "notes": [
        {
            "author": "Bob Nasution",
            "role": "Hiring Manager",
            "message": "Portofolionya oke, tapi kurang di pengalaman riset"
        }
    ],
    "education": [
        {
            "institution": "Institut Teknologi Bandung",
            "degree": "Sarjana",
            "fieldOfStudy": "Desain Grafis",
            "graduationYear": 2016,
            "gpa": 3.8
        }
    ],
    "workExperiences": [
        {
            "company": "Tokopedia",
            "position": "Senior Product Designer",
            "startDate": "2020-01-15",
            "endDate": null,
            "isCurrent": true,
            "description": "Memimpin tim desain produk untuk fitur marketplace dan payment gateway"
        },
        {
            "company": "Grab",
            "position": "Product Designer",
            "startDate": "2018-03-01",
            "endDate": "2019-12-31",
            "isCurrent": false,
            "description": "Mendesain interface pengguna untuk aplikasi mobile driver dan konsumen"
        }
    ]
}

const handleFileUpload = (event: Event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (!file) return

    isUploading.value = true
    // Simulate upload and extraction
    setTimeout(() => {
        isUploading.value = false
        isExtracting.value = true
        setTimeout(() => {
            isExtracting.value = false
            extractedData.value = dummyData
            toast.success('CV Extracted Successfully')
        }, 1500)
    }, 1000)
}

const handleSubmit = () => {
    if (selectedAction.value === 'job' && !selectedJob.value) {
        toast.error('Please select a job to apply')
        return
    }
    toast.success(selectedAction.value === 'pool' ? 'Added to Candidate Pool' : 'Application Submitted')
    // Reset or redirect
}

const formatCurrency = (value: number, currency: string) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: currency }).format(value)
}
</script>

<template>
    <div class="h-screen w-full flex flex-col p-6 overflow-hidden">
        <div class="mb-6 shrink-0">
            <h1 class="text-3xl font-bold tracking-tight">New Candidate Entry</h1>
            <p class="text-muted-foreground">Upload a CV to automatically extract candidate information.</p>
        </div>

        <div class="flex-1 overflow-y-auto min-h-0">
            <Card v-if="!extractedData && !isExtracting" class="border-dashed border-2 h-full">
                <CardContent class="flex flex-col items-center justify-center h-full text-center">
                <div class="rounded-full bg-primary/10 p-4 mb-4">
                    <Icon name="lucide:upload-cloud" class="h-10 w-10 text-primary" />
                </div>
                <h3 class="text-lg font-semibold">Upload CV / Resume</h3>
                <p class="text-sm text-muted-foreground mb-6 max-w-sm">
                    Drag and drop your file here or click to browse. Supports PDF, DOCX.
                </p>
                <div class="relative">
                    <Button :disabled="isUploading">
                        <span v-if="isUploading">Uploading...</span>
                        <span v-else>Select File</span>
                    </Button>
                    <input 
                        type="file" 
                        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                        accept=".pdf,.doc,.docx"
                        @change="handleFileUpload"
                        :disabled="isUploading"
                    />
                </div>
            </CardContent>
        </Card>

        <div v-else-if="isExtracting" class="flex flex-col items-center justify-center h-full">
            <Icon name="lucide:loader-2" class="h-12 w-12 animate-spin text-primary mb-4" />
            <h3 class="text-xl font-semibold">Extracting Data...</h3>
            <p class="text-muted-foreground">Analyzing CV content with AI</p>
        </div>

        <div v-else class="space-y-6">
            <!-- Extracted Data Review -->
            <div class="grid gap-6 md:grid-cols-3">
                <!-- Sidebar / Personal Info -->
                <Card class="md:col-span-1 h-fit">
                    <CardHeader class="text-center">
                        <div class="mx-auto bg-primary/10 h-24 w-24 rounded-full flex items-center justify-center mb-2">
                            <span class="text-3xl font-bold text-primary">{{ extractedData.name.charAt(0) }}</span>
                        </div>
                        <CardTitle>{{ extractedData.name }}</CardTitle>
                    </CardHeader>
                    <CardContent class="space-y-4">
                        <div class="space-y-1">
                            <Label class="text-xs text-muted-foreground">Email</Label>
                            <div class="text-sm truncate" :title="extractedData.email">{{ extractedData.email }}</div>
                        </div>
                        <div class="space-y-1">
                            <Label class="text-xs text-muted-foreground">Phone</Label>
                            <div class="text-sm">{{ extractedData.phone }}</div>
                        </div>
                        <div class="space-y-1">
                            <Label class="text-xs text-muted-foreground">Location</Label>
                            <div class="text-sm">{{ extractedData.address.city }}, {{ extractedData.address.country }}</div>
                        </div>
                        <Separator />
                        <div class="space-y-2">
                            <Label class="text-xs text-muted-foreground">Skills</Label>
                            <div class="flex flex-wrap gap-1">
                                <Badge v-for="skill in extractedData.skills" :key="skill" variant="secondary" class="text-xs">
                                    {{ skill }}
                                </Badge>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Main Content -->
                <div class="md:col-span-2 space-y-6">
                    <!-- Experience -->
                    <Card>
                        <CardHeader>
                            <CardTitle class="text-lg flex items-center gap-2">
                                <Icon name="lucide:briefcase" class="h-5 w-5" />
                                Work Experience
                            </CardTitle>
                        </CardHeader>
                        <CardContent class="space-y-6">
                            <div v-for="(exp, index) in extractedData.workExperiences" :key="index" class="relative pl-4 border-l-2 border-muted pb-4 last:pb-0">
                                <div class="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-primary"></div>
                                <div class="flex justify-between items-start mb-1">
                                    <div>
                                        <h4 class="font-semibold">{{ exp.position }}</h4>
                                        <div class="text-sm text-muted-foreground">{{ exp.company }}</div>
                                    </div>
                                    <Badge variant="outline" class="text-xs">
                                        {{ exp.startDate }} - {{ exp.isCurrent ? 'Present' : exp.endDate }}
                                    </Badge>
                                </div>
                                <p class="text-sm text-muted-foreground mt-2">{{ exp.description }}</p>
                            </div>
                        </CardContent>
                    </Card>

                    <!-- Education -->
                    <Card>
                        <CardHeader>
                            <CardTitle class="text-lg flex items-center gap-2">
                                <Icon name="lucide:graduation-cap" class="h-5 w-5" />
                                Education
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div v-for="(edu, index) in extractedData.education" :key="index" class="flex justify-between items-start">
                                <div>
                                    <h4 class="font-semibold">{{ edu.institution }}</h4>
                                    <div class="text-sm text-muted-foreground">{{ edu.degree }} in {{ edu.fieldOfStudy }}</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-sm font-medium">{{ edu.graduationYear }}</div>
                                    <div class="text-xs text-muted-foreground">GPA: {{ edu.gpa }}</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                </div>
            </div>

            <!-- Action Area -->
            <Card class="bg-muted/30">
                <CardHeader>
                    <CardTitle>Next Steps</CardTitle>
                    <CardDescription>Decide how to proceed with this candidate.</CardDescription>
                </CardHeader>
                <CardContent>
                    <RadioGroup v-model="selectedAction" class="grid gap-4">
                        <div class="flex items-start space-x-3 space-y-0">
                            <RadioGroupItem value="pool" id="pool" class="mt-1" />
                            <div class="grid gap-1.5">
                                <Label for="pool" class="font-medium cursor-pointer">
                                    Add to Candidate Pool
                                </Label>
                                <p class="text-sm text-muted-foreground">
                                    Save the candidate profile for future opportunities without applying to a specific job.
                                </p>
                            </div>
                        </div>
                        <div class="flex items-start space-x-3 space-y-0">
                            <RadioGroupItem value="job" id="job" class="mt-1" />
                            <div class="grid gap-1.5 w-full">
                                <Label for="job" class="font-medium cursor-pointer">
                                    Apply to Specific Job
                                </Label>
                                <p class="text-sm text-muted-foreground mb-2">
                                    Link this candidate directly to an open position.
                                </p>
                                <Select v-if="selectedAction === 'job'" v-model="selectedJob">
                                    <SelectTrigger class="w-full md:w-[300px]">
                                        <SelectValue placeholder="Select a job position" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="senior-product-designer">Senior Product Designer</SelectItem>
                                        <SelectItem value="ux-researcher">UX Researcher</SelectItem>
                                        <SelectItem value="frontend-dev">Frontend Developer</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </RadioGroup>
                </CardContent>
                <CardFooter class="flex justify-end gap-2">
                    <Button variant="outline" @click="extractedData = null">Cancel</Button>
                    <Button @click="handleSubmit">Confirm & Save</Button>
                </CardFooter>
            </Card>
        </div>
        </div>
    </div>
</template>