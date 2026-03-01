#!/usr/bin/env python3
"""
MeetAI - Admin Dashboard
"""

import sqlite3
from pathlib import Path
from typing import Dict, List


class AdminDashboard:
    def __init__(self, db_path: str = "data/meetai.db"):
        self.db_path = db_path
    
    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0] or 0
        
        c.execute("SELECT tier, COUNT(*) FROM users GROUP BY tier")
        tiers = {r[0]: r[1] for r in c.fetchall()}
        
        c.execute("SELECT SUM(amount) FROM payments")
        total_revenue = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM meetings")
        total_meetings = c.fetchone()[0] or 0
        
        c.execute("SELECT AVG(duration) FROM meetings")
        avg_duration = c.fetchone()[0] or 0
        
        conn.close()
        
        return {"users": total_users, "tiers": tiers, "revenue": total_revenue, "meetings": total_meetings, "avg_duration": avg_duration}
    
    def get_top_meetings(self, limit: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT title, platform, COUNT(*) FROM meetings GROUP BY title ORDER BY COUNT(*) DESC LIMIT ?", (limit,))
        meetings = [{"title": r[0], "platform": r[1], "count": r[2]} for r in c.fetchall()]
        conn.close()
        return meetings
    
    def print_dashboard(self):
        stats = self.get_stats()
        print("\n" + "="*50)
        print("📹  MEETAI ADMIN")
        print("="*50)
        print(f"Users: {stats['users']} | Revenue: ${stats['revenue']:.2f}")
        print(f"Meetings: {stats['meetings']} | Avg Duration: {stats['avg_duration']:.0f}min")
        print(f"Tiers: {stats['tiers']}")
        print("="*50)


if __name__ == "__main__":
    AdminDashboard().print_dashboard()
