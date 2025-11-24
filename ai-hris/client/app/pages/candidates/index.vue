<script setup lang="ts">
import { columns } from '@/components/candidates/components/columns'
import DataTable from '@/components/candidates/components/DataTable.vue'
import candidatesData from '@/components/candidates/data/candidates.json'
import type { Candidate } from '@/components/candidates/data/schema'
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div>
      <h2 class="text-3xl font-bold tracking-tight">
        Candidates
      </h2>
      <p class="text-muted-foreground mt-1">
        Manage and review candidate applications and profiles
      </p>
    </div>

    <!-- Candidates Table -->
    <DataTable :data="(candidatesData as { data: Candidate[] }).data" :columns="columns" />
  </div>
</template>