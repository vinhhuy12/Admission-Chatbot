/**
 * Root Layout
 */

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin', 'vietnamese'] })

export const metadata: Metadata = {
  title: 'Tư vấn tuyển sinh - Chatbot AI',
  description: 'Chatbot tư vấn tuyển sinh đại học thông minh sử dụng AI',
  keywords: ['tuyển sinh', 'đại học', 'chatbot', 'AI', 'tư vấn'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body className={inter.className}>{children}</body>
    </html>
  )
}

