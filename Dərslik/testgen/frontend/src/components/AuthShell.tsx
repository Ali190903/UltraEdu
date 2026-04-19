'use client'
import Link from 'next/link'
import Image from 'next/image'
import type { ReactNode } from 'react'

const features = [
  {
    title: 'DİM formatında AI generasiyası',
    desc: 'Real suallar saniyələr içində — Azərbaycan dili, Riyaziyyat, İngilis dili.',
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
    desc: 'Asan, orta və çətin sual paylanması avtomatlaşdırılmış idarə olunur.',
    icon: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"
      />
    ),
  },
  {
    title: 'PDF və Word ixracı',
    desc: 'Hazır sınaqları bir kliklə yükləyərək çap edə bilərsiniz.',
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
    <div className="min-h-screen bg-white lg:grid lg:grid-cols-2">
      {/* Left panel: Compact Academic SaaS Aesthetic - STICKY so it never has empty scroll voids */}
      <aside className="hidden lg:flex flex-col relative bg-accent-50/50 border-r border-accent-200/60 p-8 xl:p-12 h-screen sticky top-0 overflow-hidden">
        
        {/* Blurs */}
        <div className="absolute top-0 right-0 w-[30rem] h-[30rem] bg-emerald-100/40 rounded-full blur-[80px] pointer-events-none -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-[20rem] h-[20rem] bg-emerald-200/20 rounded-full blur-[60px] pointer-events-none translate-y-1/3 -translate-x-1/4" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-[0.03] pointer-events-none"></div>

        {/* Content wrapper */}
        <div className="relative z-10 w-full max-w-sm mx-auto flex flex-col h-full justify-between">
          
          <div className="flex-1 flex flex-col justify-center">
            <Link href="/" className="inline-flex items-center gap-2 w-fit group mb-10">
              <div className="rounded-lg bg-white p-1.5 shadow-sm ring-1 ring-accent-200 group-hover:shadow group-hover:ring-emerald-200 transition-all">
                <Image src="/logo.svg" alt="UltraEdu" width={28} height={28} className="opacity-90" />
              </div>
              <span className="text-lg font-bold tracking-tight">
                <span className="text-accent-900">Ultra</span>
                <span className="text-emerald-600">Edu</span>
              </span>
            </Link>

            <div className="space-y-3">
              <h2 className="font-display text-3xl xl:text-4xl leading-[1.1] font-bold tracking-tight text-accent-900">
                DİM imtahanlarına <br/> AI ilə hazırlaşın
              </h2>
              <p className="text-accent-600 text-[0.9rem] xl:text-[0.95rem] leading-relaxed max-w-sm">
                Abituriyentlər və müəllimlər üçün sürətli və qüsursuz variant generasiyası sistemi.
              </p>
            </div>

            <ul className="mt-10 space-y-5">
              {features.map((f) => (
                <li key={f.title} className="flex gap-4 group">
                  <div className="shrink-0 w-11 h-11 rounded-lg bg-white shadow-sm ring-1 ring-accent-200 flex items-center justify-center group-hover:ring-emerald-300 group-hover:bg-emerald-50 transition-all duration-300">
                    <svg
                      className="w-5 h-5 text-emerald-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      {f.icon}
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-bold text-accent-900 text-[0.85rem] xl:text-[0.9rem] tracking-tight">{f.title}</h3>
                    <p className="text-accent-500 text-[0.8rem] xl:text-[0.85rem] mt-0.5 leading-relaxed">{f.desc}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="text-[10px] xl:text-[11px] font-medium text-accent-400 uppercase tracking-widest pt-8 pb-2">
            © {new Date().getFullYear()} ULTRAEDU INC.
          </div>
        </div>
      </aside>

      {/* Right form panel - Scrolls naturally if needed */}
      <section className="relative flex flex-col items-center justify-center p-6 xl:p-12 bg-white min-h-screen">
        <div className="w-full max-w-[360px] xl:max-w-[380px] relative z-10 mx-auto flex flex-col justify-center py-8">
          
          {/* Mobile logo header */}
          <div className="lg:hidden text-center mb-8 flex flex-col items-center">
            <Link href="/" className="inline-flex items-center gap-2">
              <Image src="/logo.svg" alt="UltraEdu" width={32} height={32} />
              <span className="text-xl font-bold tracking-tight">
                <span className="text-accent-900">Ultra</span>
                <span className="text-emerald-600">Edu</span>
              </span>
            </Link>
          </div>

          <div className="w-full">
            <div className="mb-8 text-center lg:text-left">
              <h1 className="font-display text-2xl xl:text-3xl font-bold text-accent-900 leading-tight tracking-tight">
                {title}
              </h1>
              <p className="text-accent-500 font-medium text-[0.85rem] xl:text-sm mt-2">{subtitle}</p>
            </div>

            <div className="bg-transparent">
              {children}
            </div>

            <div className="mt-8 text-center text-[0.85rem] font-medium text-accent-500">
              {footer}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
