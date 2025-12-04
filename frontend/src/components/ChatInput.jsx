import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

export default function ChatInput({ onSend, disabled }) {
    const [message, setMessage] = useState('')
    const textareaRef = useRef(null)

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
        }
    }, [message])

    const handleSubmit = (e) => {
        e.preventDefault()
        if (message.trim() && !disabled) {
            onSend(message.trim())
            setMessage('')
        }
    }

    const handleKeyDown = (e) => {
        // Enter sends message, Shift+Enter for new line
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="border-t border-dark-border bg-dark-card p-4">
            <div className="max-w-4xl mx-auto flex gap-3 items-end">
                <textarea
                    ref={textareaRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about travel plans, weather, hotels, or anything travel-related..."
                    disabled={disabled}
                    rows={1}
                    className="flex-1 bg-dark-bg border border-dark-border rounded-xl px-4 py-3 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none max-h-32 disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <button
                    type="submit"
                    disabled={!message.trim() || disabled}
                    className="flex-shrink-0 bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-700 disabled:cursor-not-allowed rounded-xl p-3 transition-colors"
                >
                    <Send size={20} className="text-white" />
                </button>
            </div>
            <p className="text-xs text-zinc-500 text-center mt-2">
                Press Enter to send • Shift + Enter for new line
            </p>
        </form>
    )
}
