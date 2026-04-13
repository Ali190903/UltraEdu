'use client'
import Link from 'next/link'
import Image from 'next/image'
import type { ReactNode } from 'react'

const features = [
  {
    title: 'DIM formatında AI generasiyası',
    desc: 'Real imtahan sualları saniyələr içində — Azərbaycan dili, Riyaziyyat, İngilis dili.',
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z"
      />
    ),
  },
  {
    title: 'Çətinlik səviyyəsinə nəzarət',
    desc: 'Asan, orta və çətin paylanması ilə hər variant sizin sinifə uyğunlaşır.',
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"
      />
    ),
  },
  {
    title: 'PDF, Word və JSON ixracı',
    desc: 'Hazır variantları bir kliklə yüklə, sinfə paylama üçün optimal.',
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
      />
    ),
  },
]

export default function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-2">
      {/* Left brand panel — desktop only */}
      <aside className="hidden lg:flex relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white">
        {/* Decorative blobs */}
        <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-primary-400/20 blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[28rem] h-[28rem] rounded-full bg-primary-300/10 blur-3xl" />
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cpath fill='%23ffffff' fill-opacity='1' d='M0 0h1v1H0zm20 20h1v1h-1z'/%3E%3C/svg%3E\")",
          }}
        />

        <div className="relative z-10 flex flex-col justify-between p-12 xl:p-16 w-full">
          <Link href="/" className="inline-flex items-center gap-2.5 w-fit group">
            <div className="rounded-xl bg-white/10 backdrop-blur-sm p-1.5 ring-1 ring-white/20 group-hover:bg-white/15 transition-colors">
              <Image src="/logo.png" alt="UltraEdu" width={32} height={32} />
            </div>
            <span className="text-xl font-bold tracking-tight">
              <span className="text-white">Ultra</span>
              <span className="text-primary-100">Edu</span>
            </span>
          </Link>

          <div className="max-w-md">
            <h2 className="font-display text-4xl xl:text-[2.75rem] leading-[1.1] font-bold tracking-tight">
              DIM imtahanlarına AI ilə hazırlaşın
            </h2>
            <p className="mt-4 text-primary-50/90 text-base leading-relaxed">
              UltraEdu müəllimlərə və abituriyentlərə keyfiyyətli sual variantları yaratmağa və paylaşmağa kömək edir.
            </p>

            <ul className="mt-10 space-y-5">
              {features.map((f) => (
                <li key={f.title} className="flex gap-4">
                  <div className="shrink-0 w-10 h-10 rounded-lg bg-white/10 ring-1 ring-white/20 flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={1.75}
                    >
                      {f.icon}
                    </svg>
                  </div>
                  <div>
                    <p className="font-semibold text-white text-[0.95rem]">{f.title}</p>
                    <p className="text-sm text-primary-50/80 mt-0.5 leading-relaxed">{f.desc}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <p className="text-xs text-primary-100/70">© {new Date().getFullYear()} UltraEdu. Bütün hüquqlar qorunur.</p>
        </div>
      </aside>

      {/* Right form panel */}
      <section className="flex items-center justify-center px-4 sm:px-6 py-10 lg:py-12 bg-accent-50">
        <div className="w-full max-w-md">
          {/* Mobile logo header */}
          <div className="lg:hidden text-center mb-6">
            <Link href="/" className="inline-flex items-center gap-2">
              <Image src="/logo.png" alt="UltraEdu" width={36} height={36} />
              <span className="text-xl font-bold tracking-tight">
                <span className="text-accent-800">Ultra</span>
                <span className="text-primary-600">Edu</span>
              </span>
            </Link>
          </div>

          <div className="card p-7 sm:p-8">
            <div className="mb-7">
              <h1 className="font-display text-2xl sm:text-[1.75rem] font-bold text-accent-900 leading-tight">
                {title}
              </h1>
              <p className="text-accent-500 text-sm mt-1.5">{subtitle}</p>
            </div>

            {children}

            <div className="mt-6 text-center text-sm text-accent-500">{footer}</div>
          </div>
        </div>
      </section>
    </div>
  )
}
