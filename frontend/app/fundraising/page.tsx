'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { fundraisingApi } from '@/lib/api'
import type { CapitalReport, CapitalSource, FundraisingRole } from '@/lib/types'

const STAGES: { key: string; label: string }[] = [
    { key: 'lead', label: 'Lead' },
    { key: 'contacted', label: 'Contacted' },
    { key: 'replied', label: 'Replied' },
    { key: 'meeting', label: 'Meeting' },
    { key: 'diligence', label: 'Diligence' },
    { key: 'negotiation', label: 'Negotiation' },
    { key: 'closed', label: 'Closed' },
]

const typeColors: Record<string, string> = {
    angel: 'bg-pink-500/20 text-pink-300',
    vc: 'bg-luxor-500/20 text-luxor-300',
    corporate: 'bg-blue-500/20 text-blue-300',
    government: 'bg-green-500/20 text-green-300',
    grant: 'bg-emerald-500/20 text-emerald-300',
    accelerator: 'bg-orange-500/20 text-orange-300',
}

function fmtMoney(n: number): string {
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
    if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}k`
    return `$${n}`
}

export default function FundraisingPage() {
    const router = useRouter()
    const [report, setReport] = useState<CapitalReport | null>(null)
    const [sources, setSources] = useState<CapitalSource[]>([])
    const [roles, setRoles] = useState<FundraisingRole[]>([])
    const [launching, setLaunching] = useState<string | null>(null)

    const refresh = useCallback(async () => {
        try {
            const [r, s] = await Promise.all([
                fundraisingApi.getReport(),
                fundraisingApi.listSources(),
            ])
            setReport(r)
            setSources(s)
        } catch (e) {
            console.error(e)
        }
    }, [])

    useEffect(() => {
        refresh()
        fundraisingApi.listRoles().then(setRoles).catch(console.error)
        const id = setInterval(refresh, 15000)
        return () => clearInterval(id)
    }, [refresh])

    const launch = async (role: string) => {
        setLaunching(role)
        try {
            const res = await fundraisingApi.runAgent(role)
            router.push(`/task/${res.task_id}`)
        } catch (e) {
            console.error(e)
            setLaunching(null)
        }
    }

    const metrics = report
        ? [
            { label: 'New Investors', value: report.new_sources },
            { label: 'Qualified Targets', value: report.qualified_targets },
            { label: 'Emails Sent', value: report.emails_sent },
            { label: 'Replies', value: report.replies_received },
            { label: 'Meetings Booked', value: report.meetings_booked },
            { label: 'Grant Opportunities', value: report.grant_opportunities },
            { label: 'Total Sources', value: report.total_sources },
            { label: 'Pipeline Value', value: fmtMoney(report.pipeline_value) },
        ]
        : []

    return (
        <div className="min-h-screen p-8 max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <button onClick={() => router.push('/')} className="text-night-500 hover:text-luxor-400 text-sm mb-2">
                        ← Luxor9
                    </button>
                    <h1 className="text-3xl font-bold">
                        <span className="text-luxor-400">Capital</span> Report
                    </h1>
                    <p className="text-night-400 text-sm mt-1">Autonomous Fundraising OS</p>
                </div>
                {report?.highest_priority && (
                    <div className="glass rounded-xl p-4 max-w-xs">
                        <p className="text-xs text-night-500 uppercase tracking-wider mb-1">Action Required</p>
                        <p className="text-sm text-gray-200">{report.action_required}</p>
                    </div>
                )}
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
                {metrics.map((m) => (
                    <div key={m.label} className="glass rounded-xl p-4">
                        <p className="text-2xl font-bold text-luxor-300">{m.value}</p>
                        <p className="text-xs text-night-400 mt-1">{m.label}</p>
                    </div>
                ))}
            </div>

            {/* Launch agents */}
            <div className="mb-10">
                <h2 className="text-night-400 text-sm font-medium mb-3 uppercase tracking-wider">Launch Agent</h2>
                <div className="flex flex-wrap gap-2">
                    {roles.map((r) => (
                        <button
                            key={r.role}
                            onClick={() => launch(r.role)}
                            disabled={launching !== null}
                            title={r.description}
                            className="text-sm bg-night-900/60 hover:bg-luxor-600/30 border border-night-800 hover:border-luxor-600 rounded-lg px-3 py-2 transition-all disabled:opacity-50"
                        >
                            {launching === r.role ? 'Starting…' : r.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Pipeline */}
            <div>
                <h2 className="text-night-400 text-sm font-medium mb-3 uppercase tracking-wider">Pipeline</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {STAGES.map((stage) => {
                        const inStage = sources.filter((s) => s.pipeline_stage === stage.key)
                        if (inStage.length === 0) return null
                        return (
                            <div key={stage.key} className="glass rounded-xl p-4">
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="text-sm font-semibold text-gray-200">{stage.label}</h3>
                                    <span className="text-xs text-night-500">{inStage.length}</span>
                                </div>
                                <div className="space-y-2">
                                    {inStage.slice(0, 12).map((s) => (
                                        <div key={s.id} className="bg-night-900/50 rounded-lg p-3">
                                            <div className="flex items-start justify-between gap-2">
                                                <p className="text-sm text-gray-200 truncate">{s.name}</p>
                                                <span className="text-xs text-luxor-300 shrink-0">{s.probability_score}%</span>
                                            </div>
                                            <div className="flex items-center gap-2 mt-1.5">
                                                {s.type && (
                                                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${typeColors[s.type] || 'bg-night-800 text-night-400'}`}>
                                                        {s.type}
                                                    </span>
                                                )}
                                                {s.geography && <span className="text-[10px] text-night-500">{s.geography}</span>}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
