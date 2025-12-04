import { MessageSquare, Trash2 } from 'lucide-react'

export default function SessionItem({ session, isActive, onClick, onDelete }) {
    const handleDelete = (e) => {
        e.stopPropagation()
        onDelete(session.session_id)
    }

    return (
        <div
            onClick={onClick}
            className={`group relative px-3 py-3 rounded-lg cursor-pointer transition-all ${isActive
                    ? 'bg-indigo-600 text-white'
                    : 'bg-dark-card border border-dark-border hover:border-indigo-500 text-zinc-300'
                }`}
        >
            <div className="flex items-start gap-2">
                <MessageSquare size={16} className="flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                        {session.preview}
                    </p>
                </div>
                <button
                    onClick={handleDelete}
                    className={`opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-500/20 ${isActive ? 'text-white' : 'text-zinc-400'
                        }`}
                >
                    <Trash2 size={14} />
                </button>
            </div>
        </div>
    )
}
