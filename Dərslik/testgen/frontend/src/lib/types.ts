export interface User {
  id: string
  email: string
  full_name: string
  role: 'student' | 'teacher'
  created_at: string
}

export interface Question {
  id: string
  subject: string
  grade: number
  topic: string
  subtopic: string | null
  question_type: 'mcq' | 'matching' | 'open_ended' | 'numeric_open' | 'written_solution'
  difficulty: 'easy' | 'medium' | 'hard'
  bloom_level: string
  question_text: string
  options: Record<string, string> | null
  matching_pairs: Record<string, string> | null
  rubric: Record<string, string> | null
  correct_answer: string
  explanation: string
  latex_content: string | null
  source_reference: string
  status: string
  created_at: string
}

export interface GenerateRequest {
  subject: string
  grade: number
  topic: string
  difficulty: string
  question_type: string
}

export interface GenerateResponse {
  question: Question
  question_id: string
  attempts: number
  timing: { retrieval: number; generation: number; validation: number; total: number }
}

export interface TopicInfo {
  chapter: string
  chapter_order: number
  topic: string
  subtopic: string | null
}

export interface SubjectInfo {
  id: string
  name: string
  name_az: string
}