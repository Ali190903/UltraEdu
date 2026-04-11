import type { Metadata } from 'next'
import Navbar from '@/components/Navbar'
import Providers from '@/components/Providers'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: 'UltraEdu — AI Test Generasiyası',
  description: 'DIM imtahan suallarının süni intellekt ilə avtomatik generasiyası sistemi',
  icons: { icon: '/logo.png' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="az">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
          crossOrigin="anonymous"
        />
      </head>
      <body className="bg-accent-50 min-h-screen text-accent-800">
        <Providers>
          <Navbar />
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  )
}