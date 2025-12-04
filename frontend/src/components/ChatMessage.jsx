import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { User, Bot } from 'lucide-react'
import 'highlight.js/styles/github-dark.css'

export default function ChatMessage({ role, content }) {
    const isUser = role === 'user'

    // Ensure content is always a string
    const textContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2)

    return (
        <div className={`flex gap-4 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                    <Bot size={18} className="text-white" />
                </div>
            )}

            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser
                ? 'bg-indigo-600 text-white'
                : 'bg-dark-card border border-dark-border'
                }`}>
                {isUser ? (
                    <p className="text-sm">{textContent}</p>
                ) : (
                    <ReactMarkdown
                        className="markdown text-sm"
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                    >
                        {textContent}
                    </ReactMarkdown>
                )}
            </div>

            {isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-zinc-700 flex items-center justify-center">
                    <User size={18} className="text-white" />
                </div>
            )}
        </div>
    )
}
