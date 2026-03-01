#!/usr/bin/env python3
"""
MailAI - Core Email Generator
AI-powered email writing
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

CONFIG = {"openai_api_key": os.getenv("OPENAI_API_KEY", ""), "model": "gpt-4"}


# Email types
EMAIL_TYPES = {
    "reply": {"name": "Reply to Email", "prompt": "Write a professional reply to this email"},
    "cold_outreach": {"name": "Cold Outreach", "prompt": "Write a compelling cold outreach email"},
    "follow_up": {"name": "Follow-up", "prompt": "Write a polite follow-up email"},
    "meeting_request": {"name": "Meeting Request", "prompt": "Write a meeting request email"},
    "thank_you": {"name": "Thank You", "prompt": "Write a thank you email"},
    "introduction": {"name": "Introduction", "prompt": "Write an introduction email"},
}

# Tones
TONES = {
    "professional": "Professional and formal",
    "casual": "Friendly and casual",
    "friendly": "Warm and friendly",
    "formal": "Very formal and professional",
    "bold": "Bold and direct",
}

# Languages
LANGUAGES = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian"}


@dataclass
class EmailRequest:
    id: str
    user_id: int
    email_type: str
    subject: str
    original_email: str
    generated_email: str
    tone: str
    language: str
    created_at: str
    status: str


class EmailGenerator:
    def __init__(self):
        self.email_types = EMAIL_TYPES
        self.tones = TONES
        self.languages = LANGUAGES
    
    def get_email_types(self) -> Dict:
        return self.email_types
    
    def get_tones(self) -> Dict:
        return self.tones
    
    def get_languages(self) -> Dict:
        return self.languages
    
    async def generate_email(self, email_type: str, subject: str, original_email: str,
                          tone: str = "professional", language: str = "en") -> str:
        """Generate email using AI"""
        
        email_info = self.email_types.get(email_type, self.email_types["reply"])
        tone_info = self.tones.get(tone, self.tones["professional"])
        
        if not CONFIG["openai_api_key"]:
            return self._fallback_email(email_type, subject, tone)
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            prompt = f"""{email_info['prompt']}.

Tone: {tone_info}
Language: {self.languages.get(language, 'English')}

Original Email Subject: {subject}
Original Email: {original_email}

Write the complete email with subject line and body."""
            
            response = await openai.ChatCompletion.acreate(
                model=CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are a professional email writer. Write clear, concise, and effective emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return self._fallback_email(email_type, subject, tone)
    
    def _fallback_email(self, email_type: str, subject: str, tone: str) -> str:
        """Fallback email without AI"""
        templates = {
            "reply": f"""Subject: Re: {subject}

Dear [Name],

Thank you for your email. I appreciate you reaching out.

[Your response here]

Best regards,
[Your name]""",
            
            "cold_outreach": f"""Subject: {subject}

Hi [Name],

I hope this email finds you well. I'm reaching out because [reason].

[Value proposition]

Would you be open to a brief conversation?

Best regards,
[Your name]""",
            
            "follow_up": f"""Subject: Following up - {subject}

Hi [Name],

I wanted to follow up on my previous email regarding {subject}.

[Quick reminder]

Let me know if you have any questions.

Best regards,
[Your name]""",
            
            "meeting_request": f"""Subject: Meeting Request - {subject}

Hi [Name},

I would like to schedule a meeting to discuss {subject}.

[Proposed time/c agenda]

Would this work for you?

Best regards,
[Your name]""",
            
            "thank_you": f"""Subject: Thank You

Dear [Name],

Thank you for [specific reason].

I truly appreciate your time and consideration.

Best regards,
[Your name]""",
            
            "introduction": f"""Subject: Introduction - {subject}

Hi [Name],

My name is [Your name] from [Company]. I came across your profile and wanted to introduce myself.

[Brief intro and reason]

Would love to connect.

Best regards,
[Your name]""",
        }
        
        return templates.get(email_type, templates["reply"])


class EmailDatabase:
    def __init__(self, db_path: str = "data/mailai.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, platform TEXT, tier TEXT DEFAULT 'free',
            emails_used INTEGER DEFAULT 0, subscription_expires TEXT, lifetime_spent REAL DEFAULT 0, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY, user_id INTEGER, email_type TEXT, subject TEXT,
            original_email TEXT, generated_email TEXT, tone TEXT, language TEXT,
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
                    "emails_used": row[4], "subscription_expires": row[5], "lifetime_spent": row[6], "created_at": row[7]}
        return None
    
    def save_email(self, email: EmailRequest):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO emails (id, user_id, email_type, subject, original_email, generated_email, tone, language, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (email.id, email.user_id, email.email_type, email.subject, email.original_email,
             email.generated_email, email.tone, email.language, email.created_at, email.status))
        c.execute('UPDATE users SET emails_used = emails_used + 1 WHERE user_id = ?', (email.user_id,))
        conn.commit()
        conn.close()
    
    def get_user_emails(self, user_id: int, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, email_type, subject, tone, created_at FROM emails WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
        emails = [{"id": r[0], "type": r[1], "subject": r[2], "tone": r[3], "created": r[4]} for r in c.fetchall()]
        conn.close()
        return emails


if __name__ == "__main__":
    gen = EmailGenerator()
    print("📧 MailAI Ready")
    print("\nEmail Types:")
    for key, val in gen.get_email_types().items():
        print(f"  {key}: {val['name']}")
    print("\nTones:")
    for key, val in gen.get_tones().items():
        print(f"  {key}: {val}")
