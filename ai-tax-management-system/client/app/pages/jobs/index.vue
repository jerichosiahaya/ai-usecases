<script setup lang="ts">
import { columns } from '@/components/jobs/components/columns'
import DataTable from '@/components/jobs/components/DataTable.vue'
import jobsData from '@/components/jobs/data/jobs.json'
import type { Job } from '@/components/jobs/data/schema'
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div>
      <h2 class="text-3xl font-bold tracking-tight">
        Jobs
      </h2>
      <p class="text-muted-foreground mt-1">
        Manage and review job postings
      </p>
    </div>

    <!-- Jobs Table -->
    <DataTable :data="(jobsData as { data: Job[] }).data" :columns="columns" />
  </div>
</template>