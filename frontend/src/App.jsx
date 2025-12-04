import { useState, useRef, useEffect } from 'react'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import ThinkingSteps from './components/ThinkingSteps'
import { Plane } from 'lucide-react'

// API URL configuration - use environment variable or fallback to proxy
const API_URL = import.meta.env.VITE_API_URL || ''

const DEFAULT_SESSION_ID = 'default-session'

function App() {
    const [messages, setMessages] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [thinkingSteps, setThinkingSteps] = useState([])
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isLoading, thinkingSteps])

    const handleSendMessage = async (userMessage) => {
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setIsLoading(true)
        setThinkingSteps([])

        try {
            const response = await fetch(`${API_URL}/api/chat/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: DEFAULT_SESSION_ID
                }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6))

                        if (data.type === 'thinking') {
                            setThinkingSteps(prev => [...prev, { type: 'thinking', message: data.message }])
                        } else if (data.type === 'tool_start') {
                            setThinkingSteps(prev => [...prev, { type: 'tool_start', message: data.message }])
                        } else if (data.type === 'tool_end') {
                            setThinkingSteps(prev => [...prev, { type: 'tool_end', message: data.message }])
                        } else if (data.type === 'complete') {
                            setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
                            setThinkingSteps([])
                        } else if (data.type === 'error') {
                            throw new Error(data.message)
                        }
                    }
                }
            }
        } catch (err) {
            console.error('[ERROR]:', err)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `❌ **Error**: ${err.message || 'Failed to connect'}. Please check backend.`
            }])
            setThinkingSteps([])
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="h-screen flex flex-col bg-dark-bg">
            <header className="border-b border-dark-border bg-dark-card px-6 py-4 flex-shrink-0">
                <div className="max-w-4xl mx-auto flex items-center gap-3">
                    <div className="bg-indigo-600 p-2 rounded-lg">
                        <Plane size={24} className="text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-semibold text-white">VoyageIQ</h1>
                        <p className="text-sm text-zinc-400">Intelligent Travel Planning</p>
                    </div>
                </div>
            </header>

            <div className="flex-1 overflow-y-auto px-6 py-6">
                <div className="max-w-4xl mx-auto">
                    {messages.length === 0 && (
                        <div className="text-center mt-20">
                            <div className="bg-indigo-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <Plane size={32} className="text-white" />
                            </div>
                            <h2 className="text-2xl font-semibold text-white mb-2">Welcome to VoyageIQ</h2>
                            <p className="text-zinc-400 mb-8">Your AI-powered travel planning assistant</p>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                                <button onClick={() => handleSendMessage("What's the weather in Paris?")} className="bg-dark-card border border-dark-border hover:border-indigo-500 rounded-xl p-4 text-left transition-colors">
                                    <p className="text-sm text-white font-medium mb-1">Check Weather</p>
                                    <p className="text-xs text-zinc-400">Paris weather</p>
                                </button>
                                <button onClick={() => handleSendMessage("Plan a 3-day trip to Tokyo")} className="bg-dark-card border border-dark-border hover:border-indigo-500 rounded-xl p-4 text-left transition-colors">
                                    <p className="text-sm text-white font-medium mb-1">Plan a Trip</p>
                                    <p className="text-xs text-zinc-400">3-day Tokyo trip</p>
                                </button>
                                <button onClick={() => handleSendMessage("Hotels in London")} className="bg-dark-card border border-dark-border hover:border-indigo-500 rounded-xl p-4 text-left transition-colors">
                                    <p className="text-sm text-white font-medium mb-1">Find Hotels</p>
                                    <p className="text-xs text-zinc-400">London hotels</p>
                                </button>
                                <button onClick={() => handleSendMessage("Top attractions in Rome")} className="bg-dark-card border border-dark-border hover:border-indigo-500 rounded-xl p-4 text-left transition-colors">
                                    <p className="text-sm text-white font-medium mb-1">Discover Places</p>
                                    <p className="text-xs text-zinc-400">Rome attractions</p>
                                </button>
                            </div>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <ChatMessage key={index} role={message.role} content={message.content} />
                    ))}

                    {isLoading && thinkingSteps.length > 0 && (
                        <ThinkingSteps steps={thinkingSteps} />
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
    )
}

export default App
