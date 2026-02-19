'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { Task } from '@/lib/types'
import { timeAgo } from '@/lib/utils'

export default function HomePage() {
    const router = useRouter()
    const [input, setInput] = useState('')
    const [tasks, setTasks] = useState<Task[]>([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        api.listTasks().then(setTasks).catch(console.error)
    }, [])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || loading) return

        setLoading(true)
        try {
            const result = await api.createTask(input.trim())
            router.push(`/task/${result.task_id}`)
        } catch (err) {
            console.error(err)
            setLoading(false)
        }
    }

    const statusColors: Record<string, string> = {
        pending: 'bg-yellow-500/20 text-yellow-400',
        running: 'bg-blue-500/20 text-blue-400',
        completed: 'bg-green-500/20 text-green-400',
        failed: 'bg-red-500/20 text-red-400',
        cancelled: 'bg-gray-500/20 text-gray-400',
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-8">
            {/* Hero */}
            <div className="text-center mb-12">
                <h1 className="text-5xl font-bold mb-3">
                    <span className="text-luxor-400">LUXOR</span>
                    <span className="text-luxor-300">9</span>
                </h1>
                <p className="text-night-400 text-lg">Your AI Workforce. Multi-Agent Task Execution.</p>
            </div>

            {/* Task Input */}
            <form onSubmit={handleSubmit} className="w-full max-w-2xl mb-16">
                <div className="glass rounded-2xl p-2 glow-accent">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Describe your task... (e.g., 'Build a dashboard analyzing GitHub trending repos')"
                            className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-gray-100 placeholder:text-night-500"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="bg-luxor-600 hover:bg-luxor-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-6 py-3 rounded-xl transition-colors"
                        >
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Starting...
                                </span>
                            ) : (
                                'Execute →'
                            )}
                        </button>
                    </div>
                </div>

                {/* Example tasks */}
                <div className="flex flex-wrap gap-2 mt-4 justify-center">
                    {[
                        'Research top 10 AI startups and create a comparison report',
                        'Build a weather dashboard with React',
                        'Scrape Hacker News front page and analyze trends',
                        'Create a Python script to analyze a CSV file',
                    ].map((example) => (
                        <button
                            key={example}
                            type="button"
                            onClick={() => setInput(example)}
                            className="text-xs text-night-400 hover:text-luxor-400 bg-night-900/50 hover:bg-night-800/50 border border-night-800 hover:border-night-700 rounded-full px-3 py-1.5 transition-all"
                        >
                            {example.length > 50 ? example.slice(0, 50) + '...' : example}
                        </button>
                    ))}
                </div>
            </form>

            {/* Task History */}
            {tasks.length > 0 && (
                <div className="w-full max-w-2xl">
                    <h2 className="text-night-400 text-sm font-medium mb-4 uppercase tracking-wider">Recent Tasks</h2>
                    <div className="space-y-2">
                        {tasks.map((task) => (
                            <button
                                key={task.id}
                                onClick={() => router.push(`/task/${task.id}`)}
                                className="w-full glass rounded-xl p-4 text-left glass-hover group"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <p className="text-gray-200 group-hover:text-white truncate transition-colors">
                                            {task.description}
                                        </p>
                                        <div className="flex items-center gap-3 mt-2">
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[task.status] || statusColors.pending}`}>
                                                {task.status}
                                            </span>
                                            <span className="text-xs text-night-500">
                                                {task.total_turns} steps
                                            </span>
                                            {task.created_at && (
                                                <span className="text-xs text-night-600">
                                                    {timeAgo(task.created_at)}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <svg className="w-5 h-5 text-night-600 group-hover:text-night-400 flex-shrink-0 mt-1 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="mt-16 text-night-700 text-xs">
                Running locally • No API costs • Powered by Ollama
            </div>
        </div>
    )
}
