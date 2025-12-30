<script setup lang="ts">
import { columns } from '@/components/gl/components/columns'
import DataTable from '@/components/gl/components/DataTable.vue'
import glData from '@/components/gl/data/glTable.json'
import type { GL } from '@/components/gl/data/schema'
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div>
      <h2 class="text-3xl font-bold tracking-tight">
        GL
      </h2>
      <p class="text-muted-foreground mt-1">
        Uploaded GL transactions for review and processing
      </p>
    </div>

    <!-- GL Table -->
    <DataTable :data="(glData as { data: GL[] }).data" :columns="columns" />
  </div>
</template>