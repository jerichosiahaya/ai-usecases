<script setup lang="ts">
import { columns } from '@/components/jobs/components/columns'
import DataTable from '@/components/jobs/components/DataTable.vue'
import jobsData from '@/components/jobs/data/jobs.json'
import type { Job } from '@/components/jobs/data/schema'

const form = ref({
  urn: "7603501881",
  vendorName: "PT Jaya Obayashi",
  reference: "212STJOJKT111125",
  documentNo: "5100009487",
  poNumber: "476017993",
  documentDate: "11/04/2025",
  whtReview: "Transaction",
  diffNormal: "0.21000000834465",
  ref: "",
  firstVouching: "",
  secondReviewer: "",
  whtSlipNumber: "",
  documentType: ""
});


</script>

<template>
    
  <div class="page">
    <!-- Header -->
    <div>
      <h2 class="text-3xl font-bold tracking-tight">
        File Upload
      </h2>
      <p class="text-muted-foreground mt-1">
        Compare GL, Invoice, Tax Invoice and Final Recon
      </p>
    </div>
    <div class="body-header">
      <h2>URN : {{ form.urn }}</h2>

      <div class="actions">
        <button class="btn">Cancel</button>
        <button class="btn primary">Save</button>
        <button class="btn">Export</button>
      </div>
    </div>

    <!-- Form Body -->
    <div class="form-grid">
      <!-- LEFT COLUMN -->
      <div class="column">
        <div class="row">
          <label>Vendor Name</label>
          <span>{{ form.vendorName }}</span>
        </div>

        <div class="row">
          <label>Reference</label>
          <span>{{ form.reference }}</span>
        </div>

        <div class="row">
          <label>Document No</label>
          <span>{{ form.documentNo }}</span>
        </div>

        <div class="row">
          <label>PO Number</label>
          <span>{{ form.poNumber }}</span>
        </div>

        <div class="row">
          <label>Document Date</label>
          <span>{{ form.documentDate }}</span>
        </div>

        <div class="row">
          <label>WHT Review</label>
          <span>{{ form.whtReview }}</span>
        </div>
      </div>

      <!-- RIGHT COLUMN -->
      <div class="column">
        <div class="row">
          <label>Diff Normal</label>
          <span class="diff">{{ form.diffNormal }}</span>
        </div>

        <div class="row">
          <label>Ref</label>
          <input v-model="form.ref" placeholder="Input Text" />
        </div>

        <div class="row">
          <label>1st Vouching</label>
          <select v-model="form.firstVouching">
            <option value="">Select One</option>
            <option>Yes</option>
            <option>No</option>
          </select>
        </div>

        <div class="row">
          <label>2nd Reviewer</label>
          <select v-model="form.secondReviewer">
            <option value="">Select One</option>
            <option>Reviewer A</option>
            <option>Reviewer B</option>
          </select>
        </div>

        <div class="row">
          <label>WHT Slip Number</label>
          <input v-model="form.whtSlipNumber" placeholder="Input Text" />
        </div>

        <div class="row">
          <label>Document Type</label>
          <input v-model="form.documentType" placeholder="Input Text" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 5px 5px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont;
}

/* Header */
.body-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-top: 20px;
}

.body-header h2{
  font-weight: bold;
  font-size: 30px;
}

.actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #999;
  background: #fff;
  cursor: pointer;
  border-radius: 4px;
}

.btn.primary {
  background: #000;
  color: #fff;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.row {
  display: grid;
  grid-template-columns: 160px 1fr;
  align-items: center;
  gap: 12px;
}

label {
  font-weight: 600;
}

input,
select {
  padding: 6px 8px;
  border: 1px solid #ccc;
  border-radius: 2px;
  width: 240px;
}

.diff {
  background: red;
  color: black;
  padding: 6px 8px;
  width: fit-content;
}
</style>