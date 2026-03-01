#!/usr/bin/env python3
"""
MeetAI - Core Meeting Processor
AI meeting transcription and summarization
"""

import os
import json
import sqlite3
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "whisper_model": "base",
}


@dataclass
class Meeting:
    id: str
    user_id: int
    platform: str  # zoom, meet, teams
    title: str
    transcript: str
    summary: str
    action_items: List[str]
    duration_minutes: int
    participants: List[str]
    recording_url: str
    created_at: str
    status: str  # processing, completed, failed


class MeetingProcessor:
    """Process meeting recordings and generate summaries"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        return {
            "standard": {
                "name": "Standard Summary",
                "prompt": "Provide a comprehensive summary of the meeting including key points discussed and outcomes.",
            },
            "action": {
                "name": "Action-Oriented",
                "prompt": "Focus on action items, decisions made, and next steps. Format as a TODO list.",
            },
            "brief": {
                "name": "Quick Brief",
                "prompt": "Give a brief 3-paragraph summary suitable for quick reading.",
            },
            "decision": {
                "name": "Decision Log",
                "prompt": "Focus on decisions made, who made them, and any disagreements noted.",
            },
        }
    
    def get_templates(self) -> Dict:
        return self.templates
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Whisper"""
        if not CONFIG["openai_api_key"]:
            return "Sample transcript from meeting..."
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            # In production, use openai.Audio.transcribe
            # response = await openai.Audio.atranscribe("whisper-1", audio_file)
            return "Transcribed text would go here..."
        
        except Exception as e:
            return f"Transcription failed: {str(e)}"
    
    async def generate_summary(self, transcript: str, template: str = "standard") -> Dict:
        """Generate meeting summary using AI"""
        
        template_info = self.templates.get(template, self.templates["standard"])
        
        if not CONFIG["openai_api_key"]:
            # Fallback
            return {
                "summary": transcript[:500] + "...",
                "action_items": ["Review action items from transcript"],
                "key_points": ["Key point 1", "Key point 2"],
                "decisions": ["Decision made"],
            }
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            # Generate summary
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": template_info["prompt"]},
                    {"role": "user", "content": f"Meeting transcript:\n{transcript[:10000]}"}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            
            # Extract action items
            action_items = await self._extract_action_items(transcript)
            key_points = await self._extract_key_points(transcript)
            decisions = await self._extract_decisions(transcript)
            
            return {
                "summary": summary,
                "action_items": action_items,
                "key_points": key_points,
                "decisions": decisions,
            }
        
        except Exception as e:
            return {
                "summary": f"Summary generation failed: {str(e)}",
                "action_items": [],
                "key_points": [],
                "decisions": [],
            }
    
    async def _extract_action_items(self, transcript: str) -> List[str]:
        """Extract action items from transcript"""
        if not CONFIG["openai_api_key"]:
            return ["Follow up on project deadline", "Schedule next meeting"]
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract action items from this transcript. List as bullet points with who is responsible."},
                    {"role": "user", "content": transcript[:8000]}
                ],
                max_tokens=500
            )
            
            items = response.choices[0].message.content.split("\n")
            return [i.strip() for i in items if i.strip()]
        
        except:
            return []
    
    async def _extract_key_points(self, transcript: str) -> List[str]:
        """Extract key points"""
        if not CONFIG["openai_api_key"]:
            return ["Important discussion point 1", "Important discussion point 2"]
        return []
    
    async def _extract_decisions(self, transcript: str) -> List[str]:
        """Extract decisions made"""
        if not CONFIG["openai_api_key"]:
            return ["Decision 1: Approved budget"]
        return []
    
    async def process_meeting(self, audio_path: str = None, transcript: str = None,
                            platform: str = "zoom", title: str = "Meeting") -> Meeting:
        """Process a meeting end-to-end"""
        
        # Get transcript
        if transcript:
            full_transcript = transcript
        elif audio_path:
            full_transcript = await self.transcribe_audio(audio_path)
        else:
            full_transcript = "No transcript provided"
        
        # Generate summary
        summary_data = await self.generate_summary(full_transcript)
        
        # Create meeting object
        meeting = Meeting(
            id=str(uuid.uuid4())[:8],
            user_id=0,  # Will be set by caller
            platform=platform,
            title=title,
            transcript=full_transcript[:5000],
            summary=summary_data["summary"],
            action_items=summary_data["action_items"],
            duration_minutes=30,  # Would calculate from actual
            participants=[],  # Would extract from meeting
            recording_url="",
            created_at=datetime.now().isoformat(),
            status="completed"
        )
        
        return meeting


class MeetingDatabase:
    def __init__(self, db_path: str = "data/meetai.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, platform TEXT, tier TEXT DEFAULT 'free',
            meetings_used INTEGER DEFAULT 0, subscription_expires TEXT, lifetime_spent REAL DEFAULT 0, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY, user_id INTEGER, platform TEXT, title TEXT, transcript TEXT,
            summary TEXT, action_items TEXT, duration INTEGER, participants TEXT, recording_url TEXT,
            created_at TEXT, status TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, plan TEXT,
            stripe_payment_id TEXT, created_at TEXT)''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, platform: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (user_id, username, platform, created_at) VALUES (?, ?, ?, ?)',
            (user_id, username, platform, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {"user_id": row[0], "username": row[1], "platform": row[2], "tier": row[3],
                    "meetings_used": row[4], "subscription_expires": row[5], "lifetime_spent": row[6], "created_at": row[7]}
        return None
    
    def save_meeting(self, meeting: Meeting, user_id: int):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO meetings (id, user_id, platform, title, transcript, summary, action_items, duration, participants, recording_url, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (meeting.id, user_id, meeting.platform, meeting.title, meeting.transcript, meeting.summary,
             json.dumps(meeting.action_items), meeting.duration_minutes, json.dumps(meeting.participants),
             meeting.recording_url, meeting.created_at, meeting.status))
        
        c.execute('UPDATE users SET meetings_used = meetings_used + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def get_user_meetings(self, user_id: int, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, title, platform, summary, duration, created_at, status FROM meetings WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
        meetings = [{"id": r[0], "title": r[1], "platform": r[2], "summary": r[3][:200], "duration": r[4], "created": r[5], "status": r[6]} for r in c.fetchall()]
        conn.close()
        return meetings


if __name__ == "__main__":
    processor = MeetingProcessor()
    print("📹 MeetAI Ready")
    print("\nTemplates:")
    for key, val in processor.get_templates().items():
        print(f"  {key}: {val['name']}")
