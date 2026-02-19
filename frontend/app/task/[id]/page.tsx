'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import { useWebSocket } from '@/hooks/useWebSocket'
import { api } from '@/lib/api'
import type { Task, AgentEvent, FileInfo } from '@/lib/types'
import { cn, formatBytes } from '@/lib/utils'

type ViewTab = 'terminal' | 'browser' | 'files'

export default function TaskPage() {
    const params = useParams()
    const taskId = params.id as string

    const { events, isConnected, latestScreenshot, plan, agents, sendMessage } = useWebSocket(taskId)
    const [task, setTask] = useState<Task | null>(null)
    const [files, setFiles] = useState<FileInfo[]>([])
    const [activeTab, setActiveTab] = useState<ViewTab>('terminal')
    const [chatInput, setChatInput] = useState('')
    const [selectedFile, setSelectedFile] = useState<string | null>(null)
    const [fileContent, setFileContent] = useState<string | null>(null)

    const eventsEndRef = useRef<HTMLDivElement>(null)
    const terminalRef = useRef<HTMLDivElement>(null)

    // Load task info
    useEffect(() => {
        api.getTask(taskId).then(setTask).catch(console.error)
    }, [taskId])

    // Poll files
    useEffect(() => {
        const poll = setInterval(() => {
            api.getTaskFiles(taskId).then(data => setFiles(data.files)).catch(() => { })
        }, 3000)
        return () => clearInterval(poll)
    }, [taskId])

    // Auto-scroll events
    useEffect(() => {
        eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [events])

    // Auto-switch to browser when screenshot arrives
    useEffect(() => {
        if (latestScreenshot) setActiveTab('browser')
    }, [latestScreenshot])

    // Load file content
    useEffect(() => {
        if (selectedFile) {
            fetch(api.getFileUrl(taskId, selectedFile))
                .then(res => res.text())
                .then(setFileContent)
                .catch(() => setFileContent('(could not load file)'))
        }
    }, [selectedFile, taskId])

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault()
        if (!chatInput.trim()) return
        sendMessage(chatInput.trim())
        setChatInput('')
    }

    const isRunning = task?.status === 'running' || task?.status === 'pending'

    const taskStatus = events.find(e => e.type === 'task_complete')
        ? 'completed'
        : events.find(e => e.type === 'error')
            ? 'failed'
            : isRunning ? 'running' : task?.status || 'pending'

    return (
        <div className="h-screen flex flex-col bg-night-950">
            {/* Top Bar */}
            <header className="h-12 border-b border-night-800 flex items-center justify-between px-4 flex-shrink-0">
                <div className="flex items-center gap-3">
                    <a href="/" className="text-luxor-400 font-bold text-sm hover:text-luxor-300">
                        ← LUXOR9
                    </a>
                    <span className="text-night-700">|</span>
                    <span className="text-gray-300 text-sm truncate max-w-md">
                        {task?.description || 'Loading...'}
                    </span>
                </div>
                <div className="flex items-center gap-3">
                    <StatusBadge status={taskStatus} />
                    <span className="text-night-500 text-xs">
                        {events.filter(e => e.type === 'tool_call').length} steps
                    </span>
                    <span className={cn(
                        "w-2 h-2 rounded-full",
                        isConnected ? "bg-green-500" : "bg-red-500"
                    )} />
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel — Agent Activity */}
                <div className="w-80 border-r border-night-800 flex flex-col overflow-hidden flex-shrink-0">
                    {/* Agents */}
                    {Object.keys(agents).length > 0 && (
                        <div className="p-3 border-b border-night-800">
                            <h3 className="text-xs font-medium text-night-400 uppercase tracking-wider mb-2">Agents</h3>
                            <div className="space-y-1">
                                {Object.entries(agents).map(([name, info]) => (
                                    <div key={name} className="flex items-center gap-2 text-sm">
                                        <span className={cn(
                                            "w-1.5 h-1.5 rounded-full",
                                            info.status === 'running' ? "bg-blue-400 animate-pulse" : "bg-green-400"
                                        )} />
                                        <span className="text-gray-300">{name}</span>
                                        <span className="text-night-500 text-xs">({info.role})</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Event Stream */}
                    <div className="flex-1 overflow-y-auto p-3 space-y-2">
                        {events.map((event, i) => (
                            <EventCard key={i} event={event} />
                        ))}
                        <div ref={eventsEndRef} />

                        {events.length === 0 && isRunning && (
                            <div className="text-night-500 text-sm text-center mt-8">
                                <div className="animate-pulse">Agent is starting...</div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Center — Main View */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Tab Bar */}
                    <div className="h-10 border-b border-night-800 flex items-center px-2 gap-1 flex-shrink-0">
                        {(['terminal', 'browser', 'files'] as ViewTab[]).map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={cn(
                                    "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                                    activeTab === tab
                                        ? "bg-night-800 text-gray-200"
                                        : "text-night-500 hover:text-night-300 hover:bg-night-900"
                                )}
                            >
                                {tab === 'terminal' && '⚡ Terminal'}
                                {tab === 'browser' && '🌐 Browser'}
                                {tab === 'files' && '📁 Files'}
                            </button>
                        ))}
                    </div>

                    {/* View Content */}
                    <div className="flex-1 overflow-hidden">
                        {activeTab === 'terminal' && (
                            <TerminalView events={events} />
                        )}
                        {activeTab === 'browser' && (
                            <BrowserView screenshot={latestScreenshot} />
                        )}
                        {activeTab === 'files' && (
                            <FilesView
                                files={files}
                                taskId={taskId}
                                selectedFile={selectedFile}
                                fileContent={fileContent}
                                onSelectFile={setSelectedFile}
                            />
                        )}
                    </div>

                    {/* Plan View */}
                    {plan && (
                        <div className="h-40 border-t border-night-800 overflow-y-auto p-3 flex-shrink-0">
                            <h3 className="text-xs font-medium text-night-400 uppercase tracking-wider mb-2">📋 Plan</h3>
                            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">{plan}</pre>
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom — Chat Input */}
            <div className="border-t border-night-800 p-3 flex-shrink-0">
                <form onSubmit={handleSend} className="flex gap-2 max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder={isRunning ? "Send a message to the agent..." : "Task completed"}
                        className="flex-1 bg-night-900 border border-night-700 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder:text-night-600 outline-none focus:border-luxor-600/50 transition-colors"
                        disabled={!isRunning}
                    />
                    <button
                        type="submit"
                        disabled={!isRunning || !chatInput.trim()}
                        className="bg-luxor-600 hover:bg-luxor-500 disabled:opacity-30 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    )
}


// ═══════════════════════════════
// Sub-components
// ═══════════════════════════════

function StatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        pending: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
        running: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
        completed: 'bg-green-500/15 text-green-400 border-green-500/30',
        failed: 'bg-red-500/15 text-red-400 border-red-500/30',
        cancelled: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
    }

    return (
        <span className={cn(
            "text-xs px-2 py-0.5 rounded-full border",
            styles[status] || styles.pending
        )}>
            {status === 'running' && <span className="inline-block w-1 h-1 rounded-full bg-blue-400 animate-pulse mr-1" />}
            {status}
        </span>
    )
}


function EventCard({ event }: { event: AgentEvent }) {
    const iconMap: Record<string, string> = {
        thought: '🤔',
        tool_call: '🔧',
        tool_result: '📋',
        screenshot: '📸',
        plan_update: '📝',
        agent_spawn: '🚀',
        agent_complete: '✅',
        task_complete: '🏁',
        task_started: '▶️',
        error: '❌',
    }

    if (event.type === 'screenshot') return null // Shown in browser view

    return (
        <div className={cn(
            "rounded-lg p-2.5 text-sm",
            event.type === 'error' ? 'bg-red-500/10 border border-red-500/20' :
                event.type === 'task_complete' ? 'bg-green-500/10 border border-green-500/20' :
                    event.type === 'thought' ? 'bg-night-800/50' :
                        'bg-night-900/50'
        )}>
            <div className="flex items-start gap-2">
                <span className="text-xs mt-0.5 flex-shrink-0">{iconMap[event.type] || '•'}</span>
                <div className="min-w-0">
                    {event.agent_name && (
                        <span className="text-night-400 text-xs">{event.agent_name} • </span>
                    )}

                    {event.type === 'thought' && (
                        <p className="text-gray-300">{event.content.text?.slice(0, 300)}</p>
                    )}

                    {event.type === 'tool_call' && (
                        <div>
                            <span className="text-luxor-400 font-mono text-xs">{event.content.tool}</span>
                            <pre className="text-night-400 text-xs mt-1 overflow-hidden max-h-20">
                                {JSON.stringify(event.content.arguments, null, 2)?.slice(0, 200)}
                            </pre>
                        </div>
                    )}

                    {event.type === 'tool_result' && (
                        <div>
                            <span className={event.content.success ? 'text-green-400' : 'text-red-400'}>
                                {event.content.success ? '✓' : '✗'} {event.content.tool}
                            </span>
                            <pre className="text-night-400 text-xs mt-1 overflow-hidden max-h-32 whitespace-pre-wrap">
                                {event.content.output?.slice(0, 400)}
                            </pre>
                        </div>
                    )}

                    {event.type === 'task_complete' && (
                        <p className="text-green-300">{event.content.summary?.slice(0, 500)}</p>
                    )}

                    {event.type === 'error' && (
                        <p className="text-red-300">{event.content.error}</p>
                    )}

                    {event.type === 'agent_spawn' && (
                        <p className="text-blue-300">
                            Agent <strong>{event.content.agent_name}</strong> ({event.content.agent_role}) started: {event.content.task?.slice(0, 100)}
                        </p>
                    )}

                    {event.type === 'agent_complete' && (
                        <p className="text-green-300">
                            Agent <strong>{event.content.agent_name}</strong> completed
                        </p>
                    )}
                </div>
            </div>
        </div>
    )
}


function TerminalView({ events }: { events: AgentEvent[] }) {
    const ref = useRef<HTMLDivElement>(null)

    useEffect(() => {
        ref.current?.scrollTo(0, ref.current.scrollHeight)
    }, [events])

    const terminalEvents = events.filter(e =>
        e.type === 'tool_call' || e.type === 'tool_result' || e.type === 'thought'
    )

    return (
        <div ref={ref} className="h-full overflow-y-auto bg-night-950 p-4 font-mono text-sm">
            {terminalEvents.map((event, i) => (
                <div key={i} className="mb-3">
                    {event.type === 'thought' && (
                        <div className="text-night-400 italic">
                            # {event.content.text?.slice(0, 200)}
                        </div>
                    )}
                    {event.type === 'tool_call' && (
                        <div>
                            <span className="text-green-400">{'>'}</span>
                            <span className="text-luxor-300 ml-2">{event.content.tool}</span>
                            {event.content.tool === 'shell' && (
                                <span className="text-gray-300 ml-2">{event.content.arguments?.command}</span>
                            )}
                            {event.content.tool === 'file_write' && (
                                <span className="text-gray-300 ml-2">→ {event.content.arguments?.path}</span>
                            )}
                            {event.content.tool === 'browser_navigate' && (
                                <span className="text-blue-300 ml-2">{event.content.arguments?.url}</span>
                            )}
                        </div>
                    )}
                    {event.type === 'tool_result' && (
                        <pre className={cn(
                            "ml-4 whitespace-pre-wrap max-h-40 overflow-hidden",
                            event.content.success ? "text-night-400" : "text-red-400"
                        )}>
                            {event.content.output?.slice(0, 1000)}
                        </pre>
                    )}
                </div>
            ))}

            {events.length > 0 && !events.find(e => e.type === 'task_complete') && (
                <div className="cursor-blink text-gray-500" />
            )}
        </div>
    )
}


function BrowserView({ screenshot }: { screenshot: string | null }) {
    if (!screenshot) {
        return (
            <div className="h-full flex items-center justify-center text-night-600">
                <div className="text-center">
                    <div className="text-4xl mb-3">🌐</div>
                    <p>Browser view will appear when the agent navigates to a webpage</p>
                </div>
            </div>
        )
    }

    return (
        <div className="h-full flex items-center justify-center bg-night-950 p-4">
            <img
                src={`data:image/png;base64,${screenshot}`}
                alt="Browser screenshot"
                className="max-w-full max-h-full object-contain rounded-lg border border-night-700"
            />
        </div>
    )
}


function FilesView({
    files,
    taskId,
    selectedFile,
    fileContent,
    onSelectFile,
}: {
    files: FileInfo[]
    taskId: string
    selectedFile: string | null
    fileContent: string | null
    onSelectFile: (path: string) => void
}) {
    return (
        <div className="h-full flex">
            {/* File list */}
            <div className="w-64 border-r border-night-800 overflow-y-auto p-3">
                {files.length === 0 ? (
                    <p className="text-night-600 text-sm text-center mt-8">No files yet</p>
                ) : (
                    <div className="space-y-0.5">
                        {files.map((file) => (
                            <button
                                key={file.path}
                                onClick={() => onSelectFile(file.path)}
                                className={cn(
                                    "w-full text-left px-2 py-1.5 rounded text-sm flex items-center justify-between group",
                                    selectedFile === file.path
                                        ? "bg-luxor-600/20 text-luxor-300"
                                        : "text-gray-400 hover:bg-night-800 hover:text-gray-200"
                                )}
                            >
                                <span className="truncate">
                                    {file.path.endsWith('/') ? '📁' : '📄'} {file.path.split('/').pop()}
                                </span>
                                <span className="text-xs text-night-600 flex-shrink-0 ml-2">
                                    {formatBytes(file.size)}
                                </span>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* File content */}
            <div className="flex-1 overflow-y-auto p-4">
                {selectedFile ? (
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-mono text-night-300">{selectedFile}</h3>
                            <a
                                href={api.getFileUrl(taskId, selectedFile)}
                                download
                                className="text-xs text-luxor-400 hover:text-luxor-300"
                            >
                                Download ↓
                            </a>
                        </div>
                        <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono bg-night-900/50 rounded-lg p-4 border border-night-800">
                            {fileContent || 'Loading...'}
                        </pre>
                    </div>
                ) : (
                    <div className="text-night-600 text-sm text-center mt-8">
                        Select a file to preview
                    </div>
                )}
            </div>
        </div>
    )
}
