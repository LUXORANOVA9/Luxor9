// frontend/hooks/useWebSocket.ts

'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import type { AgentEvent } from '@/lib/types'

export function useWebSocket(taskId: string | null) {
    const [events, setEvents] = useState<AgentEvent[]>([])
    const [isConnected, setIsConnected] = useState(false)
    const [latestScreenshot, setLatestScreenshot] = useState<string | null>(null)
    const [plan, setPlan] = useState<string>('')
    const [agents, setAgents] = useState<Record<string, { role: string; status: string }>>({})
    const wsRef = useRef<WebSocket | null>(null)

    useEffect(() => {
        if (!taskId) return

        const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/task/${taskId}`
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => setIsConnected(true)
        ws.onclose = () => setIsConnected(false)

        ws.onmessage = (message) => {
            try {
                const event: AgentEvent = JSON.parse(message.data)
                setEvents(prev => [...prev, event])

                // Handle specific event types
                switch (event.type) {
                    case 'screenshot':
                        setLatestScreenshot(event.content.image)
                        break
                    case 'plan_update':
                        setPlan(event.content.plan)
                        break
                    case 'agent_spawn':
                        setAgents(prev => ({
                            ...prev,
                            [event.content.agent_name]: {
                                role: event.content.agent_role,
                                status: 'running',
                            },
                        }))
                        break
                    case 'agent_complete':
                        setAgents(prev => ({
                            ...prev,
                            [event.content.agent_name]: {
                                ...prev[event.content.agent_name],
                                status: 'completed',
                            },
                        }))
                        break
                }
            } catch (e) {
                console.error('WS parse error:', e)
            }
        }

        return () => {
            ws.close()
        }
    }, [taskId])

    const sendMessage = useCallback((content: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'user_message', content }))
        }
    }, [])

    return {
        events,
        isConnected,
        latestScreenshot,
        plan,
        agents,
        sendMessage,
    }
}
