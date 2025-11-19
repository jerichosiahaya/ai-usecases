import type { AvatarProps } from '@nuxt/ui'

export type UserStatus = 'subscribed' | 'unsubscribed' | 'bounced'
export type SaleStatus = 'paid' | 'failed' | 'refunded'

export interface User {
  id: number
  name: string
  email: string
  avatar?: AvatarProps
  status: UserStatus
  location: string
}

export interface Mail {
  id: number
  unread?: boolean
  from: User
  subject: string
  body: string
  date: string
}

export interface Member {
  name: string
  username: string
  role: 'member' | 'owner'
  avatar: AvatarProps
}

export interface Stat {
  title: string
  icon: string
  value: number | string
  variation: number
  formatter?: (value: number) => string
}

export interface Sale {
  id: string
  date: string
  status: SaleStatus
  email: string
  amount: number
}

export interface Notification {
  id: number
  unread?: boolean
  sender: User
  body: string
  date: string
}

export type Period = 'daily' | 'weekly' | 'monthly'

export interface Range {
  start: Date
  end: Date
}

export type CaseStatus = 'pending' | 'analyzing' | 'completed' | 'archived'

export interface AnalysisData {
  data_review: string
  root_cause_analysis: string
  hypothesis_testing: string
}

export interface ApplicableLaw {
  law_name: string
  articles: string[]
  violation_description: string
  penalty_level: string
}

export interface NodeInfo {
  name: string
}

export interface EdgeInfo {
  source: string
  target: string
  label: string
}

export interface KnowledgeGraph {
  nodes: Record<string, NodeInfo>
  edges: Record<string, EdgeInfo>
}

export interface FraudCase {
  id: string
  name: string
  description: string
  status: CaseStatus
  created_at: string
  files: (string | FileMetadata)[]
  analysis?: AnalysisData
  case_main_category?: string
  case_sub_category?: string
  applicable_laws?: ApplicableLaw[]
  law_impact_analysis?: string
  insights?: string[]
  recommendations?: string[]
  notes?: CaseNote[]
  knowledge_graph?: KnowledgeGraph
}

export interface CaseNote {
  id?: string
  content: string
  created_at?: string
  author?: string
}

export interface CreateCasePayload {
  name: string
  description: string
  files?: File[] | FileMetadata[]
}

export interface FileMetadata {
  url: string
  name: string
  description: string
  format: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface ChatHistory {
  id: string
  caseId: string
  caseName: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}
