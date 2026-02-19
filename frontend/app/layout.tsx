// frontend/app/layout.tsx

import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Luxor9 — AI Agent Platform',
    description: 'Your AI Workforce. Multi-agent task execution.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <body className="min-h-screen">
                {children}
            </body>
        </html>
    )
}
