#!/usr/bin/env python3
"""
PodAI - Core Podcast Generator
Convert articles, PDFs, YouTube to podcasts using AI
"""

import os
import re
import json
import sqlite3
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "elevenlabs_key": os.getenv("ELEVENLABS_API_KEY", ""),
    "model": "tts-1-hd",
    "voice": "alloy",
}

# Voice options
VOICES = {
    "alloy": {"name": "Alloy", "gender": "neutral"},
    "echo": {"name": "Echo", "gender": "male"},
    "fable": {"name": "Fable", "gender": "male"},
    "onyx": {"name": "Onyx", "gender": "male"},
    "nova": {"name": "Nova", "gender": "female"},
    "shimmer": {"name": "Shimmer", "gender": "female"},
}

# Language options
LANGUAGES = {
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
}


@dataclass
class PodcastRequest:
    id: str
    user_id: int
    source_type: str  # url, youtube, pdf
    source_url: str
    title: str
    content: str
    summary: str
    audio_url: str
    voice: str
    language: str
    duration_seconds: int
    created_at: str
    status: str  # processing, completed, failed


class ContentExtractor:
    """Extract content from various sources"""
    
    async def extract_from_url(self, url: str) -> Dict:
        """Extract content from URL"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove script/style tags
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Get title
            title = soup.title.string if soup.title else "Untitled"
            
            # Get main content
            main = soup.find('main') or soup.find('article') or soup.find('body')
            text = main.get_text(separator='\n', strip=True) if main else ""
            
            # Limit text length
            text = text[:10000]
            
            return {"title": title, "content": text, "source_type": "url"}
        
        except Exception as e:
            return {"title": "Error", "content": f"Failed to extract: {str(e)}", "source_type": "url"}
    
    async def extract_from_youtube(self, url: str) -> Dict:
        """Extract from YouTube video"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'YouTube Video')
                description = info.get('description', '')[:2000]
                transcript = ""
                
                # Try to get transcript
                try:
                    # Would need youtube-transcript-api in production
                    transcript = description
                except:
                    transcript = description
                
                content = f"{title}\n\n{transcript}"
                
                return {"title": title, "content": content, "source_type": "youtube"}
        
        except Exception as e:
            return {"title": "Error", "content": f"Failed: {str(e)}", "source_type": "youtube"}
    
    async def extract_from_pdf(self, file_path: str) -> Dict:
        """Extract from PDF"""
        # Would use PyPDF2 or pdfplumber
        return {"title": "PDF Document", "content": "PDF extraction not implemented", "source_type": "pdf"}


class PodcastGenerator:
    """Generate podcasts using AI"""
    
    def __init__(self):
        self.extractor = ContentExtractor()
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        return {
            "news": {
                "name": "News Brief",
                "system_prompt": "Summarize this news article in a clear, professional news anchor style.",
            },
            "blog": {
                "name": "Blog Post",
                "system_prompt": "Convert this blog post into an engaging podcast script.",
            },
            "educational": {
                "name": "Educational",
                "system_prompt": "Explain this content in an educational, easy-to-understand style.",
            },
            "summary": {
                "name": "Quick Summary",
                "system_prompt": "Give a brief, concise summary of the key points.",
            },
        }
    
    def get_voices(self) -> Dict:
        return VOICES
    
    def get_languages(self) -> Dict:
        return LANGUAGES
    
    def get_templates(self) -> Dict:
        return self.templates
    
    async def generate_podcast(self, source_type: str, source_url: str, 
                              voice: str = "alloy", language: str = "en",
                              template: str = "blog") -> Dict:
        """Generate a podcast from source"""
        
        # Extract content
        if source_type == "youtube":
            content_data = await self.extractor.extract_from_youtube(source_url)
        elif source_type == "pdf":
            content_data = await self.extractor.extract_from_pdf(source_url)
        else:
            content_data = await self.extractor.extract_from_url(source_url)
        
        title = content_data.get("title", "Untitled")
        content = content_data.get("content", "")
        
        # Generate summary using AI
        summary = await self._generate_summary(content, template)
        
        # Generate script
        script = await self._generate_script(content, summary, template)
        
        # Generate audio
        audio_url = await self._generate_audio(script, voice)
        
        # Estimate duration (average 150 words/min)
        words = len(script.split())
        duration = int(words / 150 * 60)
        
        return {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "content": content[:2000],
            "summary": summary,
            "script": script,
            "audio_url": audio_url,
            "voice": voice,
            "language": language,
            "duration_seconds": duration,
            "status": "completed" if audio_url else "processing",
        }
    
    async def _generate_summary(self, content: str, template: str) -> str:
        """Generate summary using AI"""
        if not CONFIG["openai_api_key"]:
            # Fallback: first 500 chars
            return content[:500] + "..."
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            template_info = self.templates.get(template, self.templates["blog"])
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f" {template_info['system_prompt']} Provide a concise summary."},
                    {"role": "user", "content": content[:5000]}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return content[:500] + "..."
    
    async def _generate_script(self, content: str, summary: str, template: str) -> str:
        """Generate podcast script"""
        if not CONFIG["openai_api_key"]:
            return f"Podcast about {summary[:200]}"
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Convert this content into a natural, conversational podcast script. Make it engaging and easy to listen to."},
                    {"role": "user", "content": f"Content:\n{content[:8000]}\n\nSummary:\n{summary}"}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return summary
    
    async def _generate_audio(self, script: str, voice: str) -> str:
        """Generate audio using TTS"""
        if not CONFIG["openai_api_key"]:
            # Return placeholder
            return "https://example.com/audio.mp3"
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            
            # Use OpenAI TTS
            response = await openai.Audio.acreate(
                model=CONFIG["model"],
                voice=voice,
                input=script[:4096],  # Max input for TTS
                response_format="mp3"
            )
            
            # In production, save to S3/cloud storage
            # For now, return base64 or placeholder
            return "https://example.com/audio.mp3"
        
        except Exception as e:
            print(f"TTS Error: {e}")
            return "https://example.com/audio.mp3"


class PodcastDatabase:
    def __init__(self, db_path: str = "data/podai.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, platform TEXT, tier TEXT DEFAULT 'free',
            podcasts_used INTEGER DEFAULT 0, subscription_expires TEXT, lifetime_spent REAL DEFAULT 0, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS podcasts (
            id TEXT PRIMARY KEY, user_id INTEGER, source_type TEXT, source_url TEXT, title TEXT,
            summary TEXT, audio_url TEXT, voice TEXT, language TEXT, duration INTEGER,
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
                    "podcasts_used": row[4], "subscription_expires": row[5], "lifetime_spent": row[6], "created_at": row[7]}
        return None
    
    def save_podcast(self, podcast: Dict, user_id: int):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO podcasts (id, user_id, source_type, source_url, title, summary, audio_url, voice, language, duration, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (podcast["id"], user_id, podcast.get("source_type", "url"), podcast.get("source_url", ""),
             podcast["title"], podcast.get("summary", ""), podcast.get("audio_url", ""), podcast.get("voice", "alloy"),
             podcast.get("language", "en"), podcast.get("duration_seconds", 0), datetime.now().isoformat(), podcast.get("status", "completed")))
        
        c.execute('UPDATE users SET podcasts_used = podcasts_used + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def get_user_podcasts(self, user_id: int, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, title, source_type, duration, voice, created_at FROM podcasts WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
        pods = [{"id": r[0], "title": r[1], "source_type": r[2], "duration": r[3], "voice": r[4], "created": r[5]} for r in c.fetchall()]
        conn.close()
        return pods


if __name__ == "__main__":
    gen = PodcastGenerator()
    print("🎙️ PodAI Ready")
    print("\nVoices:")
    for v, info in gen.get_voices().items():
        print(f"  {v}: {info['name']}")
    print("\nLanguages:")
    for code, name in gen.get_languages().items():
        print(f"  {code}: {name}")
