#!/usr/bin/env python3
"""MailAI - Admin Dashboard"""
import sqlite3
from pathlib import Path
from typing import Dict, List

class AdminDashboard:
    def __init__(self, db_path="data/mailai.db"): self.db_path = db_path
    
    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0] or 0
        c.execute("SELECT tier, COUNT(*) FROM users GROUP BY tier"); tiers = {r[0]: r[1] for r in c.fetchall()}
        c.execute("SELECT SUM(amount) FROM payments"); revenue = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM emails"); emails = c.fetchone()[0] or 0
        conn.close()
        return {"users": users, "tiers": tiers, "revenue": revenue, "emails": emails}
    
    def get_top_types(self, limit=5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT email_type, COUNT(*) FROM emails GROUP BY email_type ORDER BY COUNT(*) DESC LIMIT ?", (limit,))
        types = [{"type": r[0], "count": r[1]} for r in c.fetchall()]
        conn.close()
        return types
    
    def print_dashboard(self):
        s = self.get_stats()
        print("\n" + "="*50)
        print("📧  MAILAI ADMIN")
        print("="*50)
        print(f"Users: {s['users']} | Revenue: ${s['revenue']:.2f}")
        print(f"Emails: {s['emails']} | Tiers: {s['tiers']}")
        print("\n📧 Top Types:")
        for t in self.get_top_types(): print(f"  {t['type']}: {t['count']}")
        print("="*50)

if __name__ == "__main__": AdminDashboard().print_dashboard()
