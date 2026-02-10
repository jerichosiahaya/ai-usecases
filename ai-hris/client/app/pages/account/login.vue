<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

definePageMeta({
  layout: 'blank'
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))

  if (email.value === 'siti.nurhaliza@hotmail.com' && password.value === '12345') {
    // Set the candidate ID as requested
    const candidateId = useCookie('candidate_id')
    candidateId.value = '3f6465ac-0337-440c-b2c5-d997e4e7861d'
    
    // Save login status
    if (import.meta.client) {
      localStorage.setItem('isLoggedIn', 'true')
    }
    
    // Navigate to the account index page
    await navigateTo('/account')
  } else {
    error.value = 'Invalid email or password'
  }
  
  loading.value = false
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-1">
        <CardTitle class="text-2xl font-bold">Employee Login</CardTitle>
        <CardDescription>
          Enter your email and password to access your account
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input id="email" v-model="email" type="email" placeholder="m@example.com" required />
        </div>
        <div class="space-y-2">
          <Label for="password">Password</Label>
          <Input id="password" v-model="password" type="password" required />
        </div>
        <div v-if="error" class="text-sm text-red-500 font-medium">
          {{ error }}
        </div>
      </CardContent>
      <CardFooter>
        <Button class="w-full" @click="handleLogin" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>