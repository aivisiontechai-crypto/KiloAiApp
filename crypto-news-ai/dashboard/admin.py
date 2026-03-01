#!/usr/bin/env python3
"""CryptoAI News - Admin Dashboard"""
import sqlite3
from pathlib import Path
from typing import Dict, List

class AdminDashboard:
    def __init__(self, db_path="data/crypto_news.db"): self.db_path = db_path
    
    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0] or 0
        c.execute("SELECT tier, COUNT(*) FROM users GROUP BY tier"); tiers = {r[0]: r[1] for r in c.fetchall()}
        c.execute("SELECT SUM(amount) FROM payments"); revenue = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM news"); news = c.fetchone()[0] or 0
        c.execute("SELECT sentiment, COUNT(*) FROM news GROUP BY sentiment"); sentiments = {r[0]: r[1] for r in c.fetchall()}
        conn.close()
        return {"users": users, "tiers": tiers, "revenue": revenue, "news": news, "sentiments": sentiments}
    
    def print_dashboard(self):
        s = self.get_stats()
        print("\n" + "="*50)
        print("📰  CRYPTONEWS AI ADMIN")
        print("="*50)
        print(f"Users: {s['users']} | Revenue: ${s['revenue']:.2f}")
        print(f"Articles: {s['news']} | Tiers: {s['tiers']}")
        print("\n📈 Sentiment:")
        for sen, cnt in s['sentiments'].items(): print(f"  {sen}: {cnt}")
        print("="*50)

if __name__ == "__main__": AdminDashboard().print_dashboard()
