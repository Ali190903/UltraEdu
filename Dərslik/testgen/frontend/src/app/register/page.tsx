'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { api } from '@/lib/api'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role: 'student' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.auth.register(form)
      router.push('/login')
    } catch (err: any) {
      setError(err.message || 'Qeydiyyat mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="card p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2 mb-6">
              <Image src="/logo.png" alt="UltraEdu" width={40} height={40} />
              <span className="text-2xl font-bold">
                <span className="text-accent-800">Ultra</span>
                <span className="text-primary-600">Edu</span>
              </span>
            </Link>
            <h1 className="text-2xl font-bold text-accent-900">Hesab yaradın</h1>
            <p className="text-accent-500 text-sm mt-1">UltraEdu-ya qoşulun</p>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg mb-6 border border-red-100">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-accent-700 mb-1.5">
                Ad Soyad
              </label>
              <input
                id="full_name"
                type="text"
                placeholder="Adınız və soyadınız"
                value={form.full_name}
                onChange={e => setForm({ ...form, full_name: e.target.value })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-accent-700 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="nümunə@email.com"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-accent-700 mb-1.5">
                Şifrə
              </label>
              <input
                id="password"
                type="password"
                placeholder="Minimum 6 simvol"
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                className="input-field"
                required
                minLength={6}
              />
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-accent-700 mb-1.5">
                Rolunuz
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setForm({ ...form, role: 'student' })}
                  className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                    form.role === 'student'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-accent-200 text-accent-500 hover:border-accent-300'
                  }`}
                >
                  <div className="text-lg mb-1">
                    <svg className="w-6 h-6 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.62 48.62 0 0112 20.904a48.62 48.62 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.636 50.636 0 00-2.658-.813A59.906 59.906 0 0112 3.493a59.903 59.903 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0112 13.489a50.702 50.702 0 017.74-3.342" />
                    </svg>
                  </div>
                  Abituriyent
                </button>
                <button
                  type="button"
                  onClick={() => setForm({ ...form, role: 'teacher' })}
                  className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                    form.role === 'teacher'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-accent-200 text-accent-500 hover:border-accent-300'
                  }`}
                >
                  <div className="text-lg mb-1">
                    <svg className="w-6 h-6 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                    </svg>
                  </div>
                  Müəllim
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full text-center">
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Yüklənir...
                </span>
              ) : (
                'Qeydiyyatdan keç'
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="mt-6 text-center text-sm text-accent-500">
            Artıq hesabınız var?{' '}
            <Link href="/login" className="text-primary-600 font-medium hover:text-primary-700 transition-colors">
              Daxil olun
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}