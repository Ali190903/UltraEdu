const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }
  // Keep Bearer header as fallback during transition
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',  // Send httpOnly cookies
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || 'Request failed')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; full_name: string; role: string }) =>
      request('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: { email: string; password: string }) =>
      request<{ access_token: string }>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    logout: () =>
      request('/api/auth/logout', { method: 'POST' }),
    me: () => request<import('./types').User>('/api/auth/me'),
  },
  subjects: {
    list: () => request<import('./types').SubjectInfo[]>('/api/subjects'),
    topics: (subjectId: string, grade: number) =>
      request<import('./types').TopicInfo[]>(`/api/subjects/${subjectId}/topics?grade=${grade}`),
  },
  questions: {
    generate: (data: import('./types').GenerateRequest) =>
      request<import('./types').GenerateResponse>('/api/generation/generate', { method: 'POST', body: JSON.stringify(data) }),
    list: (params: string) => request<{ items: import('./types').Question[]; total: number }>(`/api/questions?${params}`),
  },
  variants: {
    generate: (data: any) => request<{ id: string }>('/api/variants/generate', { method: 'POST', body: JSON.stringify(data) }),
    list: () => request<any[]>('/api/variants'),
    get: (id: string) => request<any>(`/api/variants/${id}`),
    export: async (id: string, format: string) => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const res = await fetch(`${API_URL}/api/variants/${id}/export?format=${format}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include',
      })
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(error.detail || 'Export failed')
      }
      const blob = await res.blob()
      const ext = format === 'word' ? 'docx' : format === 'text' ? 'txt' : format
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `variant_${id}.${ext}`
      a.click()
      URL.revokeObjectURL(url)
    },
  },
  reports: {
    create: (data: { question_id: string; report_type: string; comment?: string }) =>
      request('/api/reports', { method: 'POST', body: JSON.stringify(data) }),
    list: (status?: string) => request<any[]>(`/api/reports${status ? `?status=${status}` : ''}`),
    resolve: (id: string, status: string) =>
      request(`/api/reports/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  },
  stats: {
    dashboard: () => request<any>('/api/stats/dashboard'),
  },
}