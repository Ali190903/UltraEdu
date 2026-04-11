'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from '@/lib/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, password)
      router.push(user.role === 'teacher' ? '/teacher/dashboard' : '/generate')
    } catch (err: any) {
      setError(err.message || 'Daxil olmaq mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4">
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
            <h1 className="text-2xl font-bold text-accent-900">Xoş gəlmisiniz</h1>
            <p className="text-accent-500 text-sm mt-1">Hesabınıza daxil olun</p>
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
              <label htmlFor="email" className="block text-sm font-medium text-accent-700 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="nümunə@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
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
                placeholder="Şifrənizi daxil edin"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="input-field"
                required
              />
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
                'Daxil ol'
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="mt-6 text-center text-sm text-accent-500">
            Hesabınız yoxdur?{' '}
            <Link href="/register" className="text-primary-600 font-medium hover:text-primary-700 transition-colors">
              Qeydiyyatdan keçin
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}