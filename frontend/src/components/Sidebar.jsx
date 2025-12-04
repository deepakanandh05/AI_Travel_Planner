import { Plus, MessageSquare } from 'lucide-react'
import SessionItem from './SessionItem'

export default function Sidebar({ sessions, activeSessionId, onSessionClick, onNewChat, onDeleteSession }) {
    return (
        <div className="w-64 bg-dark-bg border-r border-dark-border flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-dark-border">
                <button
                    onClick={onNewChat}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg px-4 py-2.5 flex items-center justify-center gap-2 transition-colors"
                >
                    <Plus size={18} />
                    <span className="font-medium">New Chat</span>
                </button>
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {sessions.length === 0 ? (
                    <div className="text-center py-8">
                        <MessageSquare size={32} className="mx-auto text-zinc-600 mb-2" />
                        <p className="text-sm text-zinc-500">No conversations yet</p>
                    </div>
                ) : (
                    sessions.map((session) => (
                        <SessionItem
                            key={session.session_id}
                            session={session}
                            isActive={session.session_id === activeSessionId}
                            onClick={() => onSessionClick(session.session_id)}
                            onDelete={onDeleteSession}
                        />
                    ))
                )}
            </div>
        </div>
    )
}
