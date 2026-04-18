'use client'
import VariantBuilder from '@/components/VariantBuilder'

export default function TeacherGeneratePage() {
  return (
    <div className="min-h-screen bg-accent-50">
      <div className="bg-white border-b border-accent-100 shadow-sm relative z-10">
        <div className="max-w-5xl mx-auto px-6 py-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div>
            <h1 className="text-2xl font-extrabold text-accent-900 tracking-tight">Variant Yarat</h1>
            <p className="text-[0.95rem] text-accent-500 mt-1">DİM formatında toplu sual generasiyası və variant yaratma</p>
          </div>
        </div>
      </div>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <VariantBuilder />
      </div>
    </div>
  )
}