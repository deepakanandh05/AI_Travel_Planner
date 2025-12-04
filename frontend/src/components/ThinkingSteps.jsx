import { Loader2 } from 'lucide-react'

export default function ThinkingSteps({ steps }) {
    if (!steps || steps.length === 0) return null

    return (
        <div className="flex gap-4 mb-6">
            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                <Loader2 size={18} className="text-white animate-spin" />
            </div>

            <div className="bg-dark-card border border-dark-border rounded-2xl px-4 py-3 flex-1">
                <div className="space-y-2">
                    {steps.map((step, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm">
                            {step.type === 'thinking' && (
                                <>
                                    <Loader2 size={14} className="text-indigo-400 animate-spin flex-shrink-0" />
                                    <span className="text-zinc-300">{step.message}</span>
                                </>
                            )}
                            {step.type === 'tool_start' && (
                                <>
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 flex-shrink-0 animate-pulse"></div>
                                    <span className="text-indigo-300">⚡ {step.message}</span>
                                </>
                            )}
                            {step.type === 'tool_end' && (
                                <>
                                    <div className="w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0"></div>
                                    <span className="text-green-300">✓ {step.message}</span>
                                </>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
