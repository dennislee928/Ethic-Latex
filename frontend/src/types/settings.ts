export interface UserSettings {
  id: number
  user_id: number
  preferences: UserPreferences
  created_at: string
  updated_at: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  default_judge_type: 'PIPELINE' | 'HUMAN' | 'COMBINED'
  auto_save: boolean
  api_base_url?: string
}

export interface ApiKey {
  id: number
  name: string
  provider: 'openai' | 'anthropic' | 'other'
  created_at: string
  last_used: string | null
  masked_key: string
}

export interface ApiKeyCreate {
  name: string
  provider: 'openai' | 'anthropic' | 'other'
  key: string
}

