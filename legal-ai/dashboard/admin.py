#!/usr/bin/env python3
"""
LegalAI - Admin Dashboard
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class AdminDashboard:
    def __init__(self, db_path: str = "data/legalai.db"):
        self.db_path = db_path
    
    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0] or 0
        
        c.execute("SELECT tier, COUNT(*) FROM users GROUP BY tier")
        tiers = {row[0]: row[1] for row in c.fetchall()}
        
        c.execute("SELECT SUM(amount) FROM payments")
        total_revenue = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM documents")
        total_docs = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_users": total_users,
            "tiers": tiers,
            "total_revenue": total_revenue,
            "total_documents": total_docs,
            "arpu": total_revenue / total_users if total_users else 0
        }
    
    def get_recent_users(self, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT user_id, username, tier, documents_used, lifetime_spent FROM users ORDER BY created_at DESC LIMIT ?", (limit,))
        users = [{"user_id": r[0], "username": r[1], "tier": r[2], "docs": r[3], "spent": r[4]} for r in c.fetchall()]
        conn.close()
        return users
    
    def get_top_docs(self, limit: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT doc_type, COUNT(*), SUM(price) FROM documents GROUP BY doc_type ORDER BY COUNT(*) DESC LIMIT ?", (limit,))
        docs = [{"type": r[0], "count": r[1], "revenue": r[2]} for r in c.fetchall()]
        conn.close()
        return docs
    
    def print_dashboard(self):
        stats = self.get_stats()
        print("\n" + "="*50)
        print("⚖️  LEGALAI ADMIN")
        print("="*50)
        print(f"Users: {stats['total_users']} | Revenue: ${stats['total_revenue']:.2f} | Docs: {stats['total_documents']}")
        print(f"Tiers: {stats['tiers']}")
        print("\n📄 Top Documents:")
        for d in self.get_top_docs():
            print(f"  {d['type']}: {d['count']} generated")
        print("\n👥 Recent Users:")
        for u in self.get_recent_users(5):
            print(f"  @{u['username']} | {u['tier']} | ${u['spent']:.2f}")
        print("="*50)


if __name__ == "__main__":
    AdminDashboard().print_dashboard()
