import '@/app/ui/global.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'BYTE.UY',
  description: 'Blog and portfolio of game developer Matias Arocena.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
    <body className={inter.className}>      
      {children}
    </body>
  </html>
  )
}
