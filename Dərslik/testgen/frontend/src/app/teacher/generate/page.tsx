'use client'
import VariantBuilder from '@/components/VariantBuilder'

export default function TeacherGeneratePage() {
  return (
    <div className="min-h-screen bg-accent-50">
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="max-w-3xl mx-auto px-6 py-8">
          <h1 className="text-2xl font-bold">Variant Yarat</h1>
          <p className="text-primary-100 mt-1">DIM formatında toplu sual generasiyası və variant yaratma</p>
        </div>
      </div>
      <div className="max-w-3xl mx-auto px-6 py-8">
        <VariantBuilder />
      </div>
    </div>
  )
}