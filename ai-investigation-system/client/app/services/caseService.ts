import type { FraudCase, CreateCasePayload } from '~/types'

const API_BASE_URL = 'https://ai-investigation-server.azurewebsites.net/api/v1'

interface ApiResponse<T> {
  status: string
  message: string
  data: T
}

const dummyCases: FraudCase[] = [
  {
    id: '1',
    name: 'Tax Fraud PT XYZ',
    description: 'Suspicious financial records showing unreported income and inflated expenses',
    status: 'completed',
    createdAt: '2025-10-15T10:30:00Z',
    files: ['tax_report_2024.pdf', 'expense_list.xlsx'],
    insights: 'Pattern identified: 40% variance in reported vs actual expenses',
    recommendations: ['Audit accounts payable', 'Review supplier contracts', 'Verify invoice authenticity']
  },
  {
    id: '2',
    name: 'Employee Embezzlement Case',
    description: 'Former finance manager transferred unauthorized funds to personal accounts',
    status: 'analyzing',
    createdAt: '2025-11-01T14:20:00Z',
    files: ['bank_statements.pdf', 'transaction_logs.csv'],
    insights: undefined,
    recommendations: undefined
  },
  {
    id: '3',
    name: 'Invoice Manipulation Scheme',
    description: 'Duplicate and modified invoices submitted for payment to shell companies',
    status: 'pending',
    createdAt: '2025-11-02T09:15:00Z',
    files: ['invoices_batch_01.pdf', 'vendor_registry.xlsx', 'payment_records.csv'],
    insights: undefined,
    recommendations: undefined
  },
  {
    id: '4',
    name: 'Asset Misappropriation',
    description: 'Company equipment and assets recorded as lost/damaged but sold privately',
    status: 'completed',
    createdAt: '2025-10-20T11:45:00Z',
    files: ['asset_log.pdf', 'maintenance_reports.docx', 'photos.zip'],
    insights: 'Identified 15 assets with duplicate damage claims within 3 months',
    recommendations: ['Implement asset tracking system', 'Require photographic evidence', 'Audit disposal records']
  },
  {
    id: '5',
    name: 'Commission Fraud Network',
    description: 'Sales staff collaborating with external parties to inflate commissions through fake transactions',
    status: 'archived',
    createdAt: '2025-09-10T16:00:00Z',
    files: ['sales_records.csv', 'commission_spreadsheet.xlsx', 'emails.zip'],
    insights: 'Network analysis shows 8 employees with coordinated activity patterns',
    recommendations: ['Terminate involved employees', 'Review commission policies', 'Implement transaction verification']
  }
]

// TODO: Replace with actual API endpoints
export const caseService = {
  async getCases(): Promise<FraudCase[]> {
    try {
      const response = await $fetch<ApiResponse<FraudCase[]>>(`${API_BASE_URL}/cases`, {
        method: 'GET'
      })
      return response.data || []
    } catch (error) {
      console.error('Error fetching cases:', error)
      return dummyCases
    }
  },

  async getCaseById(id: string): Promise<FraudCase> {
    try {
      const response = await $fetch<ApiResponse<FraudCase>>(`${API_BASE_URL}/cases/${id}`, {
        method: 'GET'
      })
      return response.data
    } catch (error) {
      console.error(`Error fetching case ${id}:`, error)
      const caseData = dummyCases.find(c => c.id === id)
      if (!caseData) throw new Error('Case not found')
      return caseData
    }
  },

  async createCase(payload: CreateCasePayload): Promise<FraudCase> {
    try {
      // Transform files to include metadata
      let filesForApi: any[] = []
      if (payload.files && Array.isArray(payload.files) && payload.files.length > 0) {
        const firstFile = payload.files[0]
        if (typeof firstFile === 'string') {
          // Old format: just strings (URLs)
          filesForApi = payload.files as any
        } else if (firstFile && 'name' in firstFile && 'format' in firstFile) {
          // New format: file metadata objects
          filesForApi = payload.files as any
        } else if (firstFile && 'name' in firstFile) {
          // File objects - extract metadata
          filesForApi = (payload.files as any).map((f: any) => ({
            name: f.name,
            description: f.description || '',
            format: f.format || ''
          }))
        }
      }

      const response = await $fetch<ApiResponse<FraudCase>>(`${API_BASE_URL}/cases`, {
        method: 'POST',
        body: {
          name: payload.name,
          description: payload.description,
          files: filesForApi,
          status: 'pending'
        }
      })
      return response.data
    } catch (error) {
      console.error('Error creating case:', error)
      throw error
    }
  },

  async updateCase(id: string, updates: Partial<FraudCase>): Promise<FraudCase> {
    try {
      const response = await $fetch<ApiResponse<FraudCase>>(`${API_BASE_URL}/cases/${id}`, {
        method: 'PUT',
        body: updates
      })
      return response.data
    } catch (error) {
      console.error(`Error updating case ${id}:`, error)
      throw error
    }
  },

  async analyzeCase(id: string): Promise<void> {
    try {
      await $fetch(`${API_BASE_URL}/cases/${id}/analysis`, {
        method: 'POST'
      })
    } catch (error) {
      console.error(`Error analyzing case ${id}:`, error)
      throw error
    }
  },

  async deleteCase(id: string): Promise<void> {
    try {
      await $fetch(`${API_BASE_URL}/cases/${id}`, {
        method: 'DELETE'
      })
    } catch (error) {
      console.error(`Error deleting case ${id}:`, error)
      throw error
    }
  },

  async addNote(id: string, content: string): Promise<any> {
    try {
      const response = await $fetch<ApiResponse<any>>(`${API_BASE_URL}/cases/${id}/notes`, {
        method: 'POST',
        body: { content }
      })
      return response.data
    } catch (error) {
      console.error(`Error adding note to case ${id}:`, error)
      throw error
    }
  },

  async deleteNote(caseId: string, noteId: string): Promise<void> {
    try {
      await $fetch(`${API_BASE_URL}/cases/${caseId}/notes/${noteId}`, {
        method: 'DELETE'
      })
    } catch (error) {
      console.error(`Error deleting note ${noteId}:`, error)
      throw error
    }
  }
}
