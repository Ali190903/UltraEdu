import Image from 'next/image'
import HomeCTA from '@/components/HomeCTA'

const subjects = [
  {
    name: 'Azərbaycan dili',
    description: '9-11-ci sinif dərsliklərindən qrammatika, leksika və oxu anlama testləri',
    icon: (
      <svg className="w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
      </svg>
    ),
  },
  {
    name: 'Riyaziyyat',
    description: 'Formullar, tənliklər, həndəsə və məntiq sualları — LaTeX dəstəyi ilə',
    icon: (
      <svg className="w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.745 3A23.933 23.933 0 003 12c0 3.183.62 6.22 1.745 9M19.5 3c.967 2.78 1.5 5.817 1.5 9s-.533 6.22-1.5 9M8.25 8.885l1.444 2.174L8.25 13.23m4.65-4.345l1.444 2.174-1.444 2.174M15.75 8.885l1.444 2.174-1.444 2.174" />
      </svg>
    ),
  },
  {
    name: 'İngilis dili',
    description: 'Grammar, vocabulary və reading comprehension — DIM formatında',
    icon: (
      <svg className="w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802" />
      </svg>
    ),
  },
]

const features = [
  {
    title: 'RAG texnologiyası',
    description: 'Dərsliklər və DIM nümunələrinə əsaslanan kontekstual sual generasiyası',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
      </svg>
    ),
  },
  {
    title: '3 mərhələli validasiya',
    description: 'Hər sual orijinallıq, düzgünlük və Bloom taksonomiyası üzrə yoxlanılır',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
      </svg>
    ),
  },
  {
    title: 'DIM standartları',
    description: '300 ballıq birinci mərhələ imtahan formatına tam uyğun suallar',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.62 48.62 0 0112 20.904a48.62 48.62 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.636 50.636 0 00-2.658-.813A59.906 59.906 0 0112 3.493a59.903 59.903 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
      </svg>
    ),
  },
  {
    title: 'Variant yaratma',
    description: 'Müəllimlər üçün tam imtahan variantı generasiyası və PDF/Word export',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
  },
]

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-100 rounded-full blur-3xl opacity-40 -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-primary-200 rounded-full blur-3xl opacity-30 translate-y-1/2 -translate-x-1/3" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-28 text-center">
          <div className="inline-flex items-center gap-2 bg-primary-100/60 text-primary-700 text-sm font-medium px-4 py-1.5 rounded-full mb-8">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
            Süni intellekt ilə test generasiyası
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6 px-2">
            <span className="text-accent-900">DİM imtahanlarına</span>
            <br />
            <span className="bg-gradient-to-r from-primary-600 to-primary-500 bg-clip-text text-transparent">
              hazırlığın yeni səviyyəsi
            </span>
          </h1>

          <p className="text-base md:text-lg lg:text-xl text-accent-500 max-w-2xl mx-auto mb-10 px-4 leading-relaxed">
            Azərbaycan dərsliklərindən süni intellekt vasitəsilə unikal,
            kurikulum əsaslı test sualları generasiya edin
          </p>

          <HomeCTA variant="hero" />
        </div>
      </section>

      {/* Subjects Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {subjects.map((subject) => (
            <div key={subject.name} className="card p-6 md:p-8 hover:border-primary-300 group cursor-default transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-14 h-14 bg-primary-50 rounded-2xl flex items-center justify-center mb-6 shadow-sm group-hover:bg-primary-100 group-hover:scale-110 transition-all duration-300">
                {subject.icon}
              </div>
              <h3 className="text-xl font-bold text-accent-900 mb-3">{subject.name}</h3>
              <p className="text-accent-600 text-[0.95rem] leading-relaxed">{subject.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
        <div className="text-center mb-16 px-2">
          <h2 className="text-3xl md:text-4xl font-bold text-accent-900 mb-5">Niyə UltraEdu?</h2>
          <p className="text-accent-600 max-w-2xl mx-auto text-base md:text-lg">
            Ən son AI texnologiyaları ilə Azərbaycanda ilk dəfə — ağıllı test generasiya sistemi
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-12">
          {features.map((feature) => (
            <div key={feature.title} className="text-center group">
              <div className="w-14 h-14 bg-primary-50 rounded-2xl flex items-center justify-center mx-auto mb-5 text-primary-600 group-hover:scale-110 group-hover:bg-primary-100 transition-all duration-300 shadow-sm">
                {feature.icon}
              </div>
              <h3 className="font-bold text-accent-900 mb-2.5 text-lg">{feature.title}</h3>
              <p className="text-[0.95rem] text-accent-600 leading-relaxed max-w-xs mx-auto">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Hazırlığınıza bu gün başlayın
          </h2>
          <p className="text-primary-100 mb-8 text-lg">
            9, 10, 11-ci sinif abituriyentləri və müəllimlər üçün
          </p>
          <HomeCTA variant="footer" />
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-accent-900 text-accent-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <Image src="/logo.png" alt="UltraEdu" width={28} height={28} />
              <span className="text-white font-bold">UltraEdu</span>
            </div>
            <p className="text-sm">
              &copy; {new Date().getFullYear()} Ultra MMC. Bütün hüquqlar qorunur.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}