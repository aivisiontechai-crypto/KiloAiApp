#!/usr/bin/env python3
"""
PodAI - Admin Dashboard
"""

import sqlite3
from pathlib import Path
from typing import Dict, List


class AdminDashboard:
    def __init__(self, db_path: str = "data/podai.db"):
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
        
        c.execute("SELECT COUNT(*) FROM podcasts")
        total_podcasts = c.fetchone()[0] or 0
        
        c.execute("SELECT AVG(duration) FROM podcasts")
        avg_duration = c.fetchone()[0] or 0
        
        conn.close()
        
        return {"users": total_users, "tiers": tiers, "revenue": total_revenue, "podcasts": total_podcasts, "avg_duration": avg_duration}
    
    def get_top_sources(self, limit: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT source_type, COUNT(*) FROM podcasts GROUP BY source_type ORDER BY COUNT(*) DESC LIMIT ?", (limit,))
        sources = [{"type": r[0], "count": r[1]} for r in c.fetchall()]
        conn.close()
        return sources
    
    def print_dashboard(self):
        stats = self.get_stats()
        print("\n" + "="*50)
        print("🎙️  PODAI ADMIN")
        print("="*50)
        print(f"Users: {stats['users']} | Revenue: ${stats['revenue']:.2f}")
        print(f"Podcasts: {stats['podcasts']} | Avg Duration: {stats['avg_duration']:.0f}s")
        print(f"Tiers: {stats['tiers']}")
        print("\n📊 Top Sources:")
        for s in self.get_top_sources():
            print(f"  {s['type']}: {s['count']}")
        print("="*50)


if __name__ == "__main__":
    AdminDashboard().print_dashboard()
