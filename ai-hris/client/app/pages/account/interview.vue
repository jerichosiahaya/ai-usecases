<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

definePageMeta({
  layout: 'blank'
})

const videoRef = ref<HTMLVideoElement | null>(null)
const stream = ref<MediaStream | null>(null)
const isCameraOpen = ref(false)
const isAiSpeaking = ref(false)
const isInterviewStarted = ref(false)
const currentQuestionIndex = ref(0)
const isFinished = ref(false)

// New Features Refs
const transcript = ref('')
const interimTranscript = ref('')
const isListening = ref(false)
const recognition = ref<any>(null)
const audioContext = ref<AudioContext | null>(null)
const analyser = ref<AnalyserNode | null>(null)
const dataArray = ref<Uint8Array | null>(null)
const audioVisualizerRef = ref<HTMLCanvasElement | null>(null)
const animationId = ref<number | null>(null)
const timer = ref(0)
const timerInterval = ref<any>(null)
const isMicMuted = ref(false)
const isVideoMuted = ref(false)

const questions = [
  "Tell me about yourself and your experience with Vue.js.",
  "What are the key differences between Options API and Composition API?",
  "How do you handle state management in a large application?",
  "Describe a challenging technical problem you solved recently."
]

const currentQuestion = ref(questions[0])

const startCamera = async () => {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
    }
    isCameraOpen.value = true
    setupAudioVisualizer()
  } catch (err) {
    console.error("Error accessing camera:", err)
    alert("Could not access camera. Please ensure you have granted permissions.")
  }
}

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
  isCameraOpen.value = false
  if (audioContext.value) {
      audioContext.value.close()
      audioContext.value = null
  }
  if (animationId.value) {
      cancelAnimationFrame(animationId.value)
  }
}

const setupRecognition = () => {
  if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    recognition.value.continuous = true
    recognition.value.interimResults = true
    recognition.value.lang = 'en-US'

    recognition.value.onresult = (event: any) => {
      let currentInterim = ''
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          transcript.value += event.results[i][0].transcript + ' '
        } else {
          currentInterim += event.results[i][0].transcript
        }
      }
      interimTranscript.value = currentInterim
    }

    recognition.value.onerror = (event: any) => {
      console.error('Speech recognition error', event.error)
      // Don't stop listening on error, just log it
    }
    
    recognition.value.onend = () => {
        if (isListening.value && !isFinished.value) {
            try {
                recognition.value.start()
            } catch (e) {
                // ignore if already started
            }
        }
    }
  } else {
    console.warn('Speech recognition not supported in this browser.')
  }
}

const startListening = () => {
    if (recognition.value) {
        try {
            recognition.value.start()
            isListening.value = true
        } catch (e) {
            console.error("Error starting recognition:", e)
        }
    }
}

const stopListening = () => {
    if (recognition.value) {
        recognition.value.stop()
        isListening.value = false
    }
}

const setupAudioVisualizer = () => {
    if (!stream.value) return

    // Wait for canvas to be available
    nextTick(() => {
        if (!audioVisualizerRef.value) return

        audioContext.value = new (window.AudioContext || (window as any).webkitAudioContext)()
        const source = audioContext.value.createMediaStreamSource(stream.value)
        analyser.value = audioContext.value.createAnalyser()
        analyser.value.fftSize = 256
        source.connect(analyser.value)
        
        const bufferLength = analyser.value.frequencyBinCount
        dataArray.value = new Uint8Array(bufferLength)
        
        const canvas = audioVisualizerRef.value
        const canvasCtx = canvas.getContext('2d')
        if (!canvasCtx) return

        const draw = () => {
            if (!analyser.value || !dataArray.value) return
            animationId.value = requestAnimationFrame(draw)
            
            analyser.value.getByteFrequencyData(dataArray.value)
            
            canvasCtx.clearRect(0, 0, canvas.width, canvas.height)
            
            const barWidth = (canvas.width / bufferLength) * 2.5
            let barHeight
            let x = 0
            
            for(let i = 0; i < bufferLength; i++) {
                barHeight = dataArray.value[i] / 2
                
                // Dynamic color based on volume
                const r = barHeight + 25 * (i/bufferLength)
                const g = 250 * (i/bufferLength)
                const b = 50
                
                canvasCtx.fillStyle = `rgb(${r},${g},${b})`
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)
                
                x += barWidth + 1
            }
        }
        
        draw()
    })
}

const startTimer = () => {
    stopTimer()
    timer.value = 0
    timerInterval.value = setInterval(() => {
        timer.value++
    }, 1000)
}

const stopTimer = () => {
    if (timerInterval.value) {
        clearInterval(timerInterval.value)
        timerInterval.value = null
    }
}

const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
}

const toggleMic = () => {
    if (stream.value) {
        isMicMuted.value = !isMicMuted.value
        stream.value.getAudioTracks().forEach(track => track.enabled = !isMicMuted.value)
    }
}

const toggleVideo = () => {
    if (stream.value) {
        isVideoMuted.value = !isVideoMuted.value
        stream.value.getVideoTracks().forEach(track => track.enabled = !isVideoMuted.value)
    }
}

const speakQuestion = () => {
  if (!('speechSynthesis' in window)) {
    alert("Text-to-speech not supported in this browser.")
    return
  }
  
  // Stop listening while AI speaks to avoid self-loop
  stopListening()
  
  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(currentQuestion.value)
  
  utterance.onstart = () => { isAiSpeaking.value = true }
  utterance.onend = () => { 
      isAiSpeaking.value = false
      // Start listening after AI finishes
      if (!isFinished.value) {
          startListening()
          startTimer()
      }
  }
  utterance.onerror = (e) => { 
      console.error("Speech synthesis error", e)
      isAiSpeaking.value = false 
      if (!isFinished.value) {
          startListening()
          startTimer()
      }
  }
  
  window.speechSynthesis.speak(utterance)
}

const startInterview = () => {
  isInterviewStarted.value = true
  speakQuestion()
}

const nextQuestion = () => {
    // Save current answer logic here (e.g., push to array)
    console.log("Answer for Q" + (currentQuestionIndex.value + 1) + ":", transcript.value)
    
    transcript.value = ''
    interimTranscript.value = ''
    stopTimer()

    if (currentQuestionIndex.value < questions.length - 1) {
        currentQuestionIndex.value++
        currentQuestion.value = questions[currentQuestionIndex.value]
        speakQuestion()
    } else {
        isFinished.value = true
        currentQuestion.value = "Thank you! The interview is complete. We will review your answers."
        speakQuestion()
        stopListening()
        stopTimer()
    }
}

onMounted(() => {
  startCamera()
  setupRecognition()
})

onUnmounted(() => {
  stopCamera()
  stopListening()
  stopTimer()
  window.speechSynthesis.cancel()
})
</script>

<template>
  <div class="flex flex-col h-[100dvh] w-full bg-background p-4 gap-4 overflow-hidden">
    <!-- Header / Status -->
    <div class="flex justify-between items-center flex-none">
      <div class="flex items-center gap-4">
          <h1 class="text-2xl font-bold tracking-tight">AI Interview Session</h1>
          <Badge v-if="isInterviewStarted && !isFinished" variant="outline" class="font-mono">
              {{ formatTime(timer) }}
          </Badge>
      </div>
      <div class="flex gap-2">
        <Badge v-if="isAiSpeaking" variant="secondary" class="animate-pulse bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">
            <Icon name="lucide:volume-2" class="w-4 h-4 mr-1" />
            AI Speaking...
        </Badge>
        <Badge v-if="isListening && !isAiSpeaking" variant="secondary" class="animate-pulse bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100">
            <Icon name="lucide:mic" class="w-4 h-4 mr-1" />
            Listening...
        </Badge>
        <Badge v-if="isCameraOpen" variant="outline" class="text-green-600 border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400">
            <Icon name="lucide:camera" class="w-4 h-4 mr-1" />
            Camera Active
        </Badge>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6 min-h-0">
      
      <!-- Camera Feed (Takes up more space) -->
      <div class="lg:col-span-2 flex flex-col gap-4 h-full min-h-0">
          <div class="relative flex-1 bg-black rounded-xl overflow-hidden shadow-lg flex items-center justify-center border border-border group min-h-0">
            <video ref="videoRef" autoplay playsinline muted class="w-full h-full object-cover transform scale-x-[-1]"></video>
            
            <div v-if="!isCameraOpen" class="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground bg-muted/50">
              <Icon name="lucide:camera-off" class="w-12 h-12 mb-2" />
              <p>Camera is off or inaccessible</p>
              <Button variant="outline" class="mt-4" @click="startCamera">Retry Camera</Button>
            </div>

            <!-- Audio Visualizer Overlay -->
            <canvas ref="audioVisualizerRef" class="absolute bottom-0 left-0 w-full h-24 opacity-50 pointer-events-none"></canvas>

            <!-- Controls Overlay (Visible on Hover) -->
            <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-black/50 p-2 rounded-full backdrop-blur-sm">
                <Button size="icon" variant="ghost" class="text-white hover:bg-white/20 rounded-full" @click="toggleMic">
                    <Icon :name="isMicMuted ? 'lucide:mic-off' : 'lucide:mic'" class="w-5 h-5" />
                </Button>
                <Button size="icon" variant="ghost" class="text-white hover:bg-white/20 rounded-full" @click="toggleVideo">
                    <Icon :name="isVideoMuted ? 'lucide:video-off' : 'lucide:video'" class="w-5 h-5" />
                </Button>
            </div>

            <!-- Overlay for user name or status -->
            <div class="absolute top-4 left-4 bg-black/50 text-white px-3 py-1 rounded-md text-sm backdrop-blur-sm">
                Candidate View
            </div>
          </div>

          <!-- Live Transcript Area -->
          <Card class="h-48 flex-none p-4 overflow-y-auto bg-muted/30 border-dashed">
              <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Live Transcript</h4>
              <p class="text-sm leading-relaxed">
                  <span class="text-foreground">{{ transcript }}</span>
                  <span class="text-muted-foreground italic">{{ interimTranscript }}</span>
              </p>
              <div v-if="!transcript && !interimTranscript && isListening" class="text-sm text-muted-foreground italic">
                  Listening for your answer...
              </div>
          </Card>
      </div>

      <!-- AI / Question Panel -->
      <div class="flex flex-col gap-4 h-full min-h-0">
        <Card class="flex-1 flex flex-col p-6 shadow-sm border-border min-h-0 overflow-y-auto">
            <div class="flex flex-col items-center text-center mb-8 mt-4 flex-none">
                <div class="relative">
                    <div class="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mb-4 ring-4 ring-primary/5 transition-all duration-300" :class="{ 'scale-110 ring-primary/20': isAiSpeaking }">
                        <Icon name="lucide:bot" class="w-12 h-12 text-primary" />
                    </div>
                    <span v-if="isAiSpeaking" class="absolute -top-1 -right-1 flex h-3 w-3">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-3 w-3 bg-sky-500"></span>
                    </span>
                </div>
                <h2 class="text-lg font-semibold">AI Interviewer</h2>
                <p class="text-sm text-muted-foreground">Automated Assessment</p>
            </div>
            
            <div class="flex-1 flex flex-col justify-center items-center text-center gap-4 min-h-0 overflow-y-auto">
                <div v-if="isInterviewStarted" class="space-y-4 w-full">
                    <div class="space-y-2">
                        <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider">Current Question {{ currentQuestionIndex + 1 }}/{{ questions.length }}</h3>
                        <p class="text-xl font-medium leading-relaxed">{{ currentQuestion }}</p>
                    </div>
                </div>
                <div v-else class="space-y-2">
                    <h3 class="text-xl font-medium">Welcome, Candidate</h3>
                    <p class="text-muted-foreground">Please ensure your camera and microphone are working before we begin.</p>
                    <div class="flex justify-center gap-4 text-sm text-muted-foreground mt-4">
                        <div class="flex items-center gap-2">
                            <Icon name="lucide:check-circle-2" class="w-4 h-4 text-green-500" /> Camera
                        </div>
                        <div class="flex items-center gap-2">
                            <Icon name="lucide:check-circle-2" class="w-4 h-4 text-green-500" /> Microphone
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-8 flex flex-col gap-3 flex-none">
                <Button v-if="!isInterviewStarted" size="lg" class="w-full" @click="startInterview">
                    <Icon name="lucide:play" class="w-4 h-4 mr-2" />
                    Start Interview
                </Button>
                
                <template v-else>
                    <Button variant="secondary" size="lg" class="w-full" @click="speakQuestion" :disabled="isAiSpeaking">
                        <Icon name="lucide:refresh-cw" class="w-4 h-4 mr-2" />
                        Repeat Question
                    </Button>
                    
                    <Button v-if="currentQuestionIndex < questions.length - 1" size="lg" class="w-full" @click="nextQuestion">
                        Next Question
                        <Icon name="lucide:arrow-right" class="w-4 h-4 ml-2" />
                    </Button>
                    <Button v-else variant="destructive" size="lg" class="w-full" @click="nextQuestion" :disabled="isFinished">
                        {{ isFinished ? 'Interview Completed' : 'Finish Interview' }}
                    </Button>
                </template>
            </div>
        </Card>
      </div>
    </div>
  </div>
</template>