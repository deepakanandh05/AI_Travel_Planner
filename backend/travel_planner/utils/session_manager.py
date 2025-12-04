"""
Session Manager for AI Travel Planner - FIXED VERSION

This version works around pickle issues by using LangGraph's SQLite saver directly
"""

import sqlite3
import os
from typing import List, Dict
from langgraph.checkpoint.sqlite import SqliteSaver


class SessionManager:
    def __init__(self, db_path: str = None):
        """Initialize session manager with database path"""
        if db_path is None:
            current_dir = os.path.dirname(__file__)
            db_path = os.path.join(current_dir, '../../data/checkpoints.db')
        
        self.db_path = db_path
        # Create connection string
        self.conn_string = f"sqlite:///{db_path}"
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all conversation sessions with metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get unique thread_ids
            cursor.execute("""
                SELECT 
                    thread_id,
                    MIN(checkpoint_id) as first_checkpoint,
                    MAX(checkpoint_id) as last_checkpoint,
                    COUNT(*) as checkpoint_count
                FROM checkpoints
                GROUP BY thread_id
                ORDER BY last_checkpoint DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                thread_id, first_cp, last_cp, count = row
                
                # Get title by reading from saver
                preview = self._get_session_title(thread_id)
                print(f"[SESSION] {thread_id[:8]}: '{preview}'")
                
                sessions.append({
                    'session_id': thread_id,
                    'preview': preview,
                    'message_count': count,
                    'created_at': first_cp,
                    'updated_at': last_cp
                })
            
            conn.close()
            print(f"[SESSION] Returning {len(sessions)} total sessions")
            return sessions
            
        except Exception as e:
            print(f"[ERROR] Error getting sessions: {e}")
            return []
    
    def _get_session_title(self, thread_id: str) -> str:
        """Get session title using LangGraph saver"""
        try:
            # Use context manager to get saver
            with SqliteSaver.from_conn_string(self.conn_string) as saver:
                config = {"configurable": {"thread_id": thread_id}}
                state = saver.get(config)
                
                if state and hasattr(state, 'values'):
                    messages = state.values.get('messages', [])
                    
                    # Find first human message
                    for msg in messages:
                        if hasattr(msg, 'type') and msg.type == 'human':
                            content = getattr(msg, 'content', '')
                            if isinstance(content, str) and content.strip():
                                return self._create_title(content)
            
            return "New Conversation"
            
        except Exception as e:
            print(f"[TITLE] Error: {e}")
            return "Conversation"
    
    def _create_title(self, text: str) -> str:
        """Create a short title from message text"""
        # Remove common prefixes
        text = text.lower().strip()
        prefixes = [
            'plan a trip to ', 'plan a ', 'i want to ',  
            'can you ', 'please ', 'tell me about ',
            'what is the weather in ', 'weather in '
        ]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        
        # Take first 3-4 words and capitalize
        words = text.strip().split()[:4]
        title = ' '.join(word.capitalize() for word in words)
        
        return title if title else "New Conversation"
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a specific session"""
        print(f"[MESSAGES] Loading session {session_id[:8]}...")
        try:
            # Use context manager to get saver
            with SqliteSaver.from_conn_string(self.conn_string) as saver:
                config = {"configurable": {"thread_id": session_id}}
                state = saver.get(config)
                
                if not state or not hasattr(state, 'values'):
                    print("[MESSAGES] No state found")
                    return []
                
                messages = state.values.get('messages', [])
                print(f"[MESSAGES] Found {len(messages)} messages in state")
                
                result = []
                for msg in messages:
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        role = 'user' if msg.type == 'human' else 'assistant'
                        content = msg.content
                        
                        # Handle Gemini list format
                        if isinstance(content, list):
                            text = ""
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    text += item['text']
                            content = text
                        
                        if content and isinstance(content, str):
                            result.append({'role': role, 'content': content})
                            print(f"[MESSAGES] {role}: {content[:50]}...")
                
                print(f"[MESSAGES] Returning {len(result)} messages")
                return result
            
        except Exception as e:
            print(f"[MESSAGES ERROR] {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (session_id,))
            cursor.execute("DELETE FROM writes WHERE thread_id = ?", (session_id,))
            
            conn.commit()
            conn.close()
            print(f"[DELETE] Deleted session {session_id[:8]}")
            return True
            
        except Exception as e:
            print(f"[DELETE ERROR] {e}")
            return False
